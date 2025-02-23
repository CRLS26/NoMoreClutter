import os
import shutil
import subprocess
import platform
import time
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import requests

icone = os.path.join(os.path.dirname(__file__), 'NoMoreClutter.ico')

class NoMoreClutter(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("NoMoreClutter")
        self.geometry("600x700")
        self.configure(bg='#f0f0f0')
        
        try:
            if os.path.exists(icone):
                self.iconbitmap(icone)
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")
        
        if not self.is_admin():
            self.request_admin_privileges()
            
        self.init_variables()

        self.create_interface()
        
    def init_variables(self):
        self.var_recycle_bin = tk.BooleanVar()
        self.var_disk_cleanup = tk.BooleanVar()
        self.var_defrag = tk.BooleanVar()
        self.var_malwarebytes = tk.BooleanVar()
        self.browser_vars = {
            'Chrome': tk.BooleanVar(),
            'Firefox': tk.BooleanVar(),
            'Edge': tk.BooleanVar(),
            'Brave': tk.BooleanVar(),
            'Vivaldi': tk.BooleanVar(),
            'Opera': tk.BooleanVar()
        }
        
        self.browser_options = {
            'cache': tk.BooleanVar(),
            'cookies': tk.BooleanVar(),
            'history': tk.BooleanVar()
        }
        
    def create_interface(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        title = ttk.Label(main_frame, 
                         text="NoMoreClutter", 
                         font=('Helvetica', 16, 'bold'))
        title.pack(pady=10)

        system_frame = ttk.LabelFrame(main_frame, text="Limpeza do Sistema")
        system_frame.pack(fill='x', pady=5)
        
        ttk.Checkbutton(system_frame, 
                       text="Limpar Lixeira",
                       variable=self.var_recycle_bin).pack(anchor='w', padx=5, pady=2)
        
        ttk.Checkbutton(system_frame,
                       text="Limpeza de Disco",
                       variable=self.var_disk_cleanup).pack(anchor='w', padx=5, pady=2)
        
        ttk.Checkbutton(system_frame,
                       text="Desfragmentar Disco (apenas HD)",
                       variable=self.var_defrag).pack(anchor='w', padx=5, pady=2)
        
        ttk.Checkbutton(system_frame,
                       text="Limpeza e remoção de virus",
                       variable=self.var_malwarebytes).pack(anchor='w', padx=5, pady=2)
        
        browser_frame = ttk.LabelFrame(main_frame, text="Limpeza de Navegadores")
        browser_frame.pack(fill='x', pady=5)

        for browser in self.browser_vars:
            ttk.Checkbutton(browser_frame,
                          text=browser,
                          variable=self.browser_vars[browser]).pack(anchor='w', padx=5, pady=2)

        options_frame = ttk.LabelFrame(browser_frame, text="Opções de Limpeza")
        options_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Checkbutton(options_frame,
                       text="Cache",
                       variable=self.browser_options['cache']).pack(anchor='w')
        
        ttk.Checkbutton(options_frame,
                       text="Cookies",
                       variable=self.browser_options['cookies']).pack(anchor='w')
        
        ttk.Checkbutton(options_frame,
                       text="Histórico",
                       variable=self.browser_options['history']).pack(anchor='w')

        self.log_text = tk.Text(main_frame, height=10, width=50)
        self.log_text.pack(pady=10)
        
        self.execute_button = ttk.Button(main_frame,
                                       text="Iniciar Limpeza",
                                       command=self.start_cleaning,
                                       padding=(20, 10))
        self.execute_button.pack(pady=10)

        self.progress = ttk.Progressbar(main_frame, 
                                      mode='determinate',
                                      length=400)
        self.progress.pack(pady=10)
        
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def request_admin_privileges(self):
        ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable," ".join(sys.argv),None,1)
        sys.exit()

    def close_chrome(self):
        try:
            self.log_text.insert(tk.END, "Fechando o Chrome...\n")
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.log_text.insert(tk.END, "✓ Chrome fechado com sucesso!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro ao fechar o Chrome: {str(e)}\n")
            return False

    def clean_chrome(self):
        try:
            self.close_chrome()

            chrome_paths = [
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2')
            ]
            
            paths_to_clean = {
                'cache': {
                    'path': '\\Cache',
                    'alt_path': '\\Cache2'
                },
                'cookies': {
                    'path': '\\Network\\Cookies',
                    'alt_path': '\\Cookies'
                },
                'history': {
                    'path': '\\History',
                    'alt_path': '\\History-journal'
                }
            }
            
            for profile_path in chrome_paths:
                if not os.path.exists(profile_path):
                    continue
                    
                self.log_text.insert(tk.END, f"\nLimpando perfil: {os.path.basename(profile_path)}\n")
                
                for option, paths in paths_to_clean.items():
                    if self.browser_options[option].get():
                        for path_type in ['path', 'alt_path']:
                            full_path = profile_path + paths[path_type]
                            try:
                                if os.path.exists(full_path):
                                    if os.path.isdir(full_path):
                                        shutil.rmtree(full_path, ignore_errors=True)
                                    else:
                                        os.remove(full_path)
                                    self.log_text.insert(tk.END, f"✓ {option.title()} limpo: {os.path.basename(full_path)}\n")
                            except Exception as e:
                                self.log_text.insert(tk.END, f"× Erro ao limpar {option}: {str(e)}\n")

            cache_path = os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\ShaderCache')
            if os.path.exists(cache_path):
                try:
                    shutil.rmtree(cache_path, ignore_errors=True)
                    self.log_text.insert(tk.END, "✓ Cache de shaders limpo\n")
                except Exception as e:
                    self.log_text.insert(tk.END, f"× Erro ao limpar cache de shaders: {str(e)}\n")
            
            self.log_text.insert(tk.END, "✓ Limpeza do Chrome concluída!\n")
            self.log_text.see(tk.END)
            return True
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro geral na limpeza do Chrome: {str(e)}\n")
            self.log_text.see(tk.END)
            return False

    def clean_recycle_bin(self):
        try:
            self.log_text.insert(tk.END, "Limpando a Lixeira...\n")
            
            drives = ['C:', 'D:', 'E:', 'F:', 'G:']
            for drive in drives:
                recycle_path = f"{drive}\\$Recycle.bin"
                if os.path.exists(recycle_path):
                    try:
                        subprocess.run(['rd', '/s', '/q', recycle_path], 
                                     shell=True, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
                    except:
                        continue

            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)
            
            self.log_text.insert(tk.END, "✓ Lixeira limpa com sucesso!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro ao limpar a Lixeira: {str(e)}\n")
            return False

    def close_firefox(self):
        try:
            self.log_text.insert(tk.END, "Fechando o Firefox...\n")
            subprocess.run(['taskkill', '/F', '/IM', 'firefox.exe'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.log_text.insert(tk.END, "✓ Firefox fechado com sucesso!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro ao fechar o Firefox: {str(e)}\n")
            return False

    def clean_firefox(self):
        try:
            self.close_firefox()
            
            firefox_path = os.path.expanduser('~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles')
            
            if not os.path.exists(firefox_path):
                self.log_text.insert(tk.END, "! Firefox não encontrado no sistema\n")
                return False
            
            profile_dirs = [d for d in os.listdir(firefox_path) if d.endswith('.default') or d.endswith('.default-release')]
            
            for profile in profile_dirs:
                profile_path = os.path.join(firefox_path, profile)
                self.log_text.insert(tk.END, f"\nLimpando perfil: {profile}\n")
                
                paths_to_clean = {
                    'cache': {
                        'path': '\\cache2',
                        'alt_path': '\\Cache'
                    },
                    'cookies': {
                        'path': '\\cookies.sqlite',
                        'alt_path': '\\cookies.sqlite-journal'
                    },
                    'history': {
                        'path': '\\places.sqlite',
                        'alt_path': '\\places.sqlite-journal'
                    }
                }
                
                for option, paths in paths_to_clean.items():
                    if self.browser_options[option].get():
                        for path_type in ['path', 'alt_path']:
                            full_path = profile_path + paths[path_type]
                            try:
                                if os.path.exists(full_path):
                                    if os.path.isdir(full_path):
                                        shutil.rmtree(full_path, ignore_errors=True)
                                    else:
                                        os.remove(full_path)
                                    self.log_text.insert(tk.END, f"✓ {option.title()} limpo: {os.path.basename(full_path)}\n")
                            except Exception as e:
                                self.log_text.insert(tk.END, f"× Erro ao limpar {option}: {str(e)}\n")
                
            self.log_text.insert(tk.END, "✓ Limpeza do Firefox concluída!\n")
            self.log_text.see(tk.END)
            return True
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro geral na limpeza do Firefox: {str(e)}\n")
            self.log_text.see(tk.END)
            return False

    def close_edge(self):
        try:
            self.log_text.insert(tk.END, "Fechando o Edge...\n")
            subprocess.run(['taskkill', '/F', '/IM', 'msedge.exe'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.log_text.insert(tk.END, "✓ Edge fechado com sucesso!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro ao fechar o Edge: {str(e)}\n")
            return False

    def clean_edge(self):
        try:
            self.close_edge()
            
            edge_paths = [
                os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default'),
                os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 1'),
                os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 2')
            ]
            
            paths_to_clean = {
                'cache': {
                    'path': '\\Cache',
                    'alt_path': '\\Cache2'
                },
                'cookies': {
                    'path': '\\Network\\Cookies',
                    'alt_path': '\\Cookies'
                },
                'history': {
                    'path': '\\History',
                    'alt_path': '\\History-journal'
                }
            }
            
            for profile_path in edge_paths:
                if not os.path.exists(profile_path):
                    continue
                    
                self.log_text.insert(tk.END, f"\nLimpando perfil Edge: {os.path.basename(profile_path)}\n")
                
                for option, paths in paths_to_clean.items():
                    if self.browser_options[option].get():
                        for path_type in ['path', 'alt_path']:
                            full_path = profile_path + paths[path_type]
                            try:
                                if os.path.exists(full_path):
                                    if os.path.isdir(full_path):
                                        shutil.rmtree(full_path, ignore_errors=True)
                                    else:
                                        os.remove(full_path)
                                    self.log_text.insert(tk.END, f"✓ {option.title()} limpo: {os.path.basename(full_path)}\n")
                            except Exception as e:
                                self.log_text.insert(tk.END, f"× Erro ao limpar {option}: {str(e)}\n")
            
            self.log_text.insert(tk.END, "✓ Limpeza do Edge concluída!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro na limpeza do Edge: {str(e)}\n")
            return False

    def close_brave(self):
        try:
            self.log_text.insert(tk.END, "Fechando o Brave...\n")
            subprocess.run(['taskkill', '/F', '/IM', 'brave.exe'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.log_text.insert(tk.END, "✓ Brave fechado com sucesso!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro ao fechar o Brave: {str(e)}\n")
            return False

    def clean_brave(self):
        try:
            self.close_brave()
            
            brave_paths = [
                os.path.expanduser('~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default'),
                os.path.expanduser('~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Profile 1'),
                os.path.expanduser('~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Profile 2')
            ]
            
            paths_to_clean = {
                'cache': {
                    'path': '\\Cache',
                    'alt_path': '\\Cache2'
                },
                'cookies': {
                    'path': '\\Network\\Cookies',
                    'alt_path': '\\Cookies'
                },
                'history': {
                    'path': '\\History',
                    'alt_path': '\\History-journal'
                }
            }
            
            for profile_path in brave_paths:
                if not os.path.exists(profile_path):
                    continue
                    
                self.log_text.insert(tk.END, f"\nLimpando perfil Brave: {os.path.basename(profile_path)}\n")
                
                for option, paths in paths_to_clean.items():
                    if self.browser_options[option].get():
                        for path_type in ['path', 'alt_path']:
                            full_path = profile_path + paths[path_type]
                            try:
                                if os.path.exists(full_path):
                                    if os.path.isdir(full_path):
                                        shutil.rmtree(full_path, ignore_errors=True)
                                    else:
                                        os.remove(full_path)
                                    self.log_text.insert(tk.END, f"✓ {option.title()} limpo: {os.path.basename(full_path)}\n")
                            except Exception as e:
                                self.log_text.insert(tk.END, f"× Erro ao limpar {option}: {str(e)}\n")
            
            self.log_text.insert(tk.END, "✓ Limpeza do Brave concluída!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro na limpeza do Brave: {str(e)}\n")
            return False

    def close_opera(self):
        try:
            self.log_text.insert(tk.END, "Fechando o Opera...\n")
            subprocess.run(['taskkill', '/F', '/IM', 'opera.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.log_text.insert(tk.END, "✓ Opera fechado com sucesso!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro ao fechar o Opera: {str(e)}\n")
            return False

    def clean_opera(self):
        try:
            self.close_opera()
            
            opera_paths = [
                os.path.expanduser('~\\AppData\\Roaming\\Opera Software\\Opera Stable'),
                os.path.expanduser('~\\AppData\\Local\\Opera Software\\Opera Stable')
            ]
            
            paths_to_clean = {
                'cache': {
                    'path': '\\Cache',
                    'alt_path': '\\GPUCache'
                },
                'cookies': {
                    'path': '\\Cookies',
                    'alt_path': '\\Network\\Cookies'
                },
                'history': {
                    'path': '\\History',
                    'alt_path': '\\History-journal'
                }
            }
            
            for profile_path in opera_paths:
                if not os.path.exists(profile_path):
                    continue
                    
                self.log_text.insert(tk.END, f"\nLimpando perfil Opera: {os.path.basename(profile_path)}\n")
                
                for option, paths in paths_to_clean.items():
                    if self.browser_options[option].get():
                        for path_type in ['path', 'alt_path']:
                            full_path = profile_path + paths[path_type]
                            try:
                                if os.path.exists(full_path):
                                    if os.path.isdir(full_path):
                                        shutil.rmtree(full_path, ignore_errors=True)
                                    else:
                                        os.remove(full_path)
                                    self.log_text.insert(tk.END, f"✓ {option.title()} limpo: {os.path.basename(full_path)}\n")
                            except Exception as e:
                                self.log_text.insert(tk.END, f"× Erro ao limpar {option}: {str(e)}\n")
            
            self.log_text.insert(tk.END, "✓ Limpeza do Opera concluída!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro na limpeza do Opera: {str(e)}\n")
            return False

    def close_vivaldi(self):

        try:
            self.log_text.insert(tk.END, "Fechando o Vivaldi...\n")
            subprocess.run(['taskkill', '/F', '/IM', 'vivaldi.exe'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.log_text.insert(tk.END, "✓ Vivaldi fechado com sucesso!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro ao fechar o Vivaldi: {str(e)}\n")
            return False

    def clean_vivaldi(self):
        try:
            self.close_vivaldi()
            
            vivaldi_paths = [
                os.path.expanduser('~\\AppData\\Local\\Vivaldi\\User Data\\Default'),
                os.path.expanduser('~\\AppData\\Local\\Vivaldi\\User Data\\Profile 1'),
                os.path.expanduser('~\\AppData\\Local\\Vivaldi\\User Data\\Profile 2')
            ]
            
            paths_to_clean = {
                'cache': {
                    'path': '\\Cache',
                    'alt_path': '\\Cache2'
                },
                'cookies': {
                    'path': '\\Network\\Cookies',
                    'alt_path': '\\Cookies'
                },
                'history': {
                    'path': '\\History',
                    'alt_path': '\\History-journal'
                }
            }
            
            for profile_path in vivaldi_paths:
                if not os.path.exists(profile_path):
                    continue
                    
                self.log_text.insert(tk.END, f"\nLimpando perfil Vivaldi: {os.path.basename(profile_path)}\n")
                
                for option, paths in paths_to_clean.items():
                    if self.browser_options[option].get():
                        for path_type in ['path', 'alt_path']:
                            full_path = profile_path + paths[path_type]
                            try:
                                if os.path.exists(full_path):
                                    if os.path.isdir(full_path):
                                        shutil.rmtree(full_path, ignore_errors=True)
                                    else:
                                        os.remove(full_path)
                                    self.log_text.insert(tk.END, f"✓ {option.title()} limpo: {os.path.basename(full_path)}\n")
                            except Exception as e:
                                self.log_text.insert(tk.END, f"× Erro ao limpar {option}: {str(e)}\n")
            
            self.log_text.insert(tk.END, "✓ Limpeza do Vivaldi concluída!\n")
            return True
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro na limpeza do Vivaldi: {str(e)}\n")
            return False

    def check_malwarebytes_installed(self):
        try:
            paths = [
                "C:\\Program Files\\Malwarebytes\\Anti-Malware\\mbam.exe",
                "C:\\Program Files (x86)\\Malwarebytes\\Anti-Malware\\mbam.exe"
            ]
            return any(os.path.exists(path) for path in paths)
        except:
            return False

    def download_malwarebytes(self):
        try:
            self.log_text.insert(tk.END, "Baixando Malwarebytes...\n")
            url = "https://downloads.malwarebytes.com/file/mb4_offline"
            
            download_path = os.path.join(os.environ['TEMP'], "mb4_offline.exe")
            
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.log_text.insert(tk.END, "✓ Download concluído!\n")
            return download_path
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro ao baixar Malwarebytes: {str(e)}\n")
            return None

    def install_malwarebytes(self, installer_path):
        try:
            self.log_text.insert(tk.END, "Instalando Malwarebytes...\n")
            install_args = [
                installer_path,
                "/VERYSILENT",
                "/SUPPRESSMSGBOXES",
                "/NORESTART",
                "/SP-",
                "/NOCANCEL",
                "/FORCECLOSEAPPLICATIONS",
                "/CLOSEAPPLICATIONS",
                "/NOICONS"
            ]

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                install_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            process.wait()

            time.sleep(30)
            
            self.log_text.insert(tk.END, "✓ Instalação concluída!\n")
            return True
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro na instalação: {str(e)}\n")
            return False

    def setup_malwarebytes_api(self):
        try:
            self.log_text.insert(tk.END, "Iniciando configuração da API do Malwarebytes...\n")

            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.log_text.insert(tk.END, "× ERRO: Necessário privilégios de administrador\n")
                return False
            
            self.log_text.insert(tk.END, "✓ Privilégios de administrador verificados\n")

            mb_paths = [
                "C:\\Program Files\\Malwarebytes\\Anti-Malware",
                "C:\\Program Files (x86)\\Malwarebytes\\Anti-Malware"
            ]
            
            self.log_text.insert(tk.END, "Procurando instalação do Malwarebytes...\n")
            mb_path = next((path for path in mb_paths if os.path.exists(path)), None)
            
            if not mb_path or not os.path.exists(os.path.join(mb_path, "mbam_api.dll")):
                self.log_text.insert(tk.END, "API não encontrada. Tentando reinstalar Malwarebytes...\n")
                installer_path = self.download_malwarebytes()
                if installer_path and self.install_malwarebytes(installer_path):
                    mb_path = next((path for path in mb_paths if os.path.exists(path)), None)
                else:
                    return False
            
            self.log_text.insert(tk.END, f"✓ Malwarebytes encontrado em: {mb_path}\n")
            return True
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× ERRO na configuração da API: {str(e)}\n")
            return False

    def run_malwarebytes_scan(self):
        try:
            self.log_text.insert(tk.END, "Iniciando varredura do Malwarebytes...\n")

            mbam_paths = [
                os.path.join("C:\\Program Files\\Malwarebytes\\Anti-Malware", "mb-cli.exe"),
                os.path.join("C:\\Program Files\\Malwarebytes", "mb-cli.exe"),
                os.path.join("C:\\Program Files (x86)\\Malwarebytes\\Anti-Malware", "mb-cli.exe"),
                os.path.join("C:\\Program Files\\Malwarebytes\\Anti-Malware", "mbam.exe"),
                os.path.join("C:\\Program Files (x86)\\Malwarebytes\\Anti-Malware", "mbam.exe")
            ]

            mbam_path = next((path for path in mbam_paths if os.path.exists(path)), None)
            
            if not mbam_path:
                self.log_text.insert(tk.END, "× Executável do Malwarebytes não encontrado\n")
                return False
            
            self.log_text.insert(tk.END, f"Usando Malwarebytes em: {mbam_path}\n")

            try:
                subprocess.run(['net', 'stop', 'MBAMService'], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
                time.sleep(2)
            except:
                pass
            
            if mbam_path.endswith('mb-cli.exe'):
                scan_args = [
                    mbam_path,
                    'scan',
                    '--threat',
                    '--quiet'
                ]
            else:
                scan_args = [
                    mbam_path,
                    '/scan',
                    '-silent',
                    '-threat'
                ]
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            self.log_text.insert(tk.END, "Iniciando varredura rápida...\n")
            start_time = time.time()
            
            process = subprocess.Popen(
                scan_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
                universal_newlines=True
            )

            while process.poll() is None:
                elapsed_time = int(time.time() - start_time)
                minutes = elapsed_time // 60
                seconds = elapsed_time % 60

                self.log_text.delete("end-2c linestart", "end-1c")
                self.log_text.insert(tk.END, f"Tempo decorrido: {minutes}m {seconds}s\n")

                output = process.stdout.readline()
                if output:
                    self.log_text.insert(tk.END, output)
                
                self.log_text.see(tk.END)
                time.sleep(1)
            
            try:
                subprocess.run(['net', 'start', 'MBAMService'], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            except:
                pass
            
            if process.returncode == 0:
                self.log_text.insert(tk.END, "✓ Varredura concluída com sucesso!\n")
                return True
            else:
                error = process.stderr.read()
                self.log_text.insert(tk.END, f"× Erro na varredura: {error}\n")
                return False
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro na varredura: {str(e)}\n")
            return False

    def clean_malwarebytes(self):
        try:
            if not self.check_malwarebytes_installed():
                self.log_text.insert(tk.END, "Malwarebytes não encontrado. Iniciando instalação...\n")
                installer_path = self.download_malwarebytes()
                if not installer_path:
                    return False
                
                if not self.install_malwarebytes(installer_path):
                    return False
                
                try:
                    os.remove(installer_path)
                except:
                    pass
            
            return self.run_malwarebytes_scan()
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro no processo do Malwarebytes: {str(e)}\n")
            return False

    def clean_disk(self):
        try:
            self.log_text.insert(tk.END, "Iniciando Limpeza de Disco...\n")

            cleanmgr_path = os.path.join(os.environ['SystemRoot'], 'System32', 'cleanmgr.exe')
            
            if not os.path.exists(cleanmgr_path):
                self.log_text.insert(tk.END, "× Ferramenta de Limpeza de Disco não encontrada\n")
                return False
            
            try:
                subprocess.run([
                    'reg', 'add', 
                    'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VolumeCaches\\Temporary Files', 
                    '/v', 'StateFlags0001', '/t', 'REG_DWORD', '/d', '2', '/f'
                ], capture_output=True)
            except:
                pass

            process = subprocess.Popen(
                [cleanmgr_path, '/sagerun:1'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=subprocess.STARTUPINFO(),
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.log_text.insert(tk.END, "Limpeza de Disco em andamento...\n")

            start_time = time.time()
            while process.poll() is None:
                elapsed_time = int(time.time() - start_time)
                minutes = elapsed_time // 60
                seconds = elapsed_time % 60
                
                self.log_text.delete("end-2c linestart", "end-1c")
                self.log_text.insert(tk.END, f"Tempo decorrido: {minutes}m {seconds}s\n")
                self.log_text.see(tk.END)
                
                time.sleep(1)
            
            if process.returncode == 0:
                self.log_text.insert(tk.END, "✓ Limpeza de Disco concluída com sucesso!\n")
                return True
            else:
                error = process.stderr.read().decode('utf-8', errors='ignore')
                self.log_text.insert(tk.END, f"× Erro na Limpeza de Disco: {error}\n")
                return False
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro na Limpeza de Disco: {str(e)}\n")
            return False

    def is_ssd(self, drive):
        try:
            cmd = f'wmic diskdrive where "DeviceID like \'%{drive[0]}%\'" get MediaType'
            result = subprocess.check_output(cmd, shell=True).decode()
            return 'SSD' in result.upper()
        except:
            return False

    def defrag_disk(self):
        try:
            self.log_text.insert(tk.END, "Iniciando Desfragmentação de Disco...\n")
            
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.log_text.insert(tk.END, "× Necessário privilégios de administrador\n")
                return False
            
            drives = []
            for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
                if os.path.exists(f'{letter}:'):
                    drives.append(f'{letter}:')
            
            if not drives:
                self.log_text.insert(tk.END, "× Nenhum drive encontrado\n")
                return False
            
            self.log_text.insert(tk.END, f"Drives encontrados: {', '.join(drives)}\n")
            
            for drive in drives:
                try:
                    if ctypes.windll.kernel32.GetDriveTypeW(drive) != 3:
                        continue
                    
                    if self.is_ssd(drive):
                        self.log_text.insert(tk.END, f"Drive {drive} é SSD - Desfragmentação não recomendada\n")
                        continue
                    
                    self.log_text.insert(tk.END, f"\nAnalisando drive {drive}...\n")
                    
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    analyze_process = subprocess.Popen(
                        ['defrag', drive, '/A'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        startupinfo=startupinfo,
                        encoding='cp437',
                        errors='ignore'
                    )
                    
                    while analyze_process.poll() is None:
                        output = analyze_process.stdout.readline()
                        if output:
                            self.log_text.insert(tk.END, output)
                            self.log_text.see(tk.END)
                    
                    if analyze_process.returncode == 0:
                        self.log_text.insert(tk.END, f"Desfragmentando drive {drive}...\n")
                        
                        defrag_process = subprocess.Popen(
                            ['defrag', drive, '/U', '/V'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            startupinfo=startupinfo,
                            encoding='cp437',
                            errors='ignore'
                        )
                        
                        start_time = time.time()
                        
                        while defrag_process.poll() is None:
                            elapsed_time = int(time.time() - start_time)
                            minutes = elapsed_time // 60
                            seconds = elapsed_time % 60
                            
                            output = defrag_process.stdout.readline()
                            if output:
                                self.log_text.insert(tk.END, output)
                            
                            self.log_text.delete("end-2c linestart", "end-1c")
                            self.log_text.insert(tk.END, f"Tempo decorrido: {minutes}m {seconds}s\n")
                            self.log_text.see(tk.END)
                            
                            time.sleep(1)
                        
                        if defrag_process.returncode == 0:
                            self.log_text.insert(tk.END, f"✓ Drive {drive} desfragmentado com sucesso!\n")
                        else:
                            error = defrag_process.stderr.read()
                            self.log_text.insert(tk.END, f"× Erro ao desfragmentar drive {drive}: {error}\n")
                    
                except Exception as e:
                    self.log_text.insert(tk.END, f"× Erro no drive {drive}: {str(e)}\n")
            
            self.log_text.insert(tk.END, "✓ Processo de desfragmentação concluído!\n")
            return True
            
        except Exception as e:
            self.log_text.insert(tk.END, f"× Erro na desfragmentação: {str(e)}\n")
            return False

    def start_cleaning(self):
        def run_cleaning():
            try:
                self.execute_button.configure(state='disabled')

                total_tasks = 0
                completed_tasks = 0
                
                if self.var_recycle_bin.get(): total_tasks += 1
                if self.var_disk_cleanup.get(): total_tasks += 1
                if self.var_defrag.get(): total_tasks += 1
                if self.var_malwarebytes.get(): total_tasks += 1
                for browser in self.browser_vars:
                    if self.browser_vars[browser].get(): total_tasks += 1
                
                if total_tasks == 0:
                    messagebox.showwarning("Aviso", "Selecione pelo menos uma tarefa!")
                    self.execute_button.configure(state='normal')
                    return

                if self.var_recycle_bin.get():
                    self.clean_recycle_bin()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()

                if self.var_disk_cleanup.get():
                    self.clean_disk()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()

                if self.browser_vars['Chrome'].get():
                    self.clean_chrome()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()
                    
                if self.browser_vars['Firefox'].get():
                    self.clean_firefox()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()
                    
                if self.browser_vars['Edge'].get():
                    self.clean_edge()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()
                    
                if self.browser_vars['Brave'].get():
                    self.clean_brave()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()
                    
                if self.browser_vars['Opera'].get():
                    self.clean_opera()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()
                    
                if self.browser_vars['Vivaldi'].get():
                    self.clean_vivaldi()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()
                
                if self.var_malwarebytes.get():
                    self.clean_malwarebytes()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()
                
                if self.var_defrag.get():
                    self.defrag_disk()
                    completed_tasks += 1
                    self.progress['value'] = (completed_tasks / total_tasks) * 100
                    self.update_idletasks()
                
            except Exception as e:
                self.log_text.insert(tk.END, f"\n× Erro durante a limpeza: {str(e)}\n")
            finally:
                self.execute_button.configure(state='normal')
                self.log_text.insert(tk.END, "\nTodas as tarefas foram concluídas!\n")
                self.log_text.see(tk.END)
                messagebox.showinfo("Concluído", "Processo de limpeza finalizado!")
        
        threading.Thread(target=run_cleaning, daemon=True).start()

    def show_error(self, title, message):
        try:
            if os.path.exists(icone):
                messagebox.showerror(title, message, icon=icone)
            else:
                messagebox.showerror(title, message)
        except:
            messagebox.showerror(title, message)

    def show_info(self, title, message):
        try:
            if os.path.exists(icone):
                messagebox.showinfo(title, message, icon=icone)
            else:
                messagebox.showinfo(title, message)
        except:
            messagebox.showinfo(title, message)

if __name__ == "__main__":
    app = NoMoreClutter()
    app.mainloop()
