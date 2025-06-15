#!/usr/bin/env python3
"""
Git Exposure Scanner v1.5 - by chor4o
Versão corrigida com:
- Verificação DNS prévia
- Timeout ajustável
- Fallback para HTTP
- Verificação mais agressiva de .git
"""

import requests
import socket
import argparse
import re
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurações
TIMEOUT = 10  # Aumentado para 10 segundos
USER_AGENT = "GitExposureScanner/1.5"
GIT_FILES = ["HEAD", "config", "index", "description"]
THEME_PATTERNS = [
    r'/wp-content/themes/([^/]+)/',
    r'/themes/([^/]+)/',
    r'"template":"([^"]+)"'
]

# Cores
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def resolve_dns(domain):
    """Verifica se o domínio resolve para um endereço IP"""
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def check_url(url):
    """Verifica se a URL é acessível"""
    try:
        response = requests.head(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
        return response.status_code < 400
    except:
        return False

def normalize_url(url):
    """Normaliza a URL"""
    url = url.strip().lower()
    if '*' in url:
        url = url.replace('*.', '')
    if not url.startswith(('http://', 'https://')):
        return f"https://{url}"
    return url

def find_theme(url):
    """Tenta identificar o tema WordPress"""
    try:
        response = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
        html = response.text
        
        for pattern in THEME_PATTERNS:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        return None
    except:
        return None

def scan_git(url, theme):
    """Varredura agressiva por .git exposto"""
    base_paths = [
        f"/wp-content/themes/{theme}/.git/",
        f"/themes/{theme}/.git/",
        "/.git/"  # Adicionado verificação na raiz também
    ]
    
    for base_path in base_paths:
        for git_file in GIT_FILES:
            target_url = urljoin(url, base_path + git_file)
            try:
                response = requests.get(
                    target_url,
                    timeout=TIMEOUT,
                    headers={"User-Agent": USER_AGENT},
                    allow_redirects=False
                )
                
                if response.status_code == 200:
                    content = response.text
                    # Verificação mais robusta dos arquivos .git
                    if git_file == "HEAD" and "ref:" in content:
                        return True, target_url
                    elif git_file == "config" and "[core]" in content:
                        return True, target_url
                    elif git_file == "description" and "Unnamed repository" in content:
                        return True, target_url
                    elif git_file == "index" and "DIRC" in content[:4]:  # Assinatura do arquivo index
                        return True, target_url
            except requests.exceptions.RequestException as e:
                print(f"{YELLOW}[!] Erro ao acessar {target_url}: {str(e)}{RESET}")
                continue
    return False, None

def process_domain(domain):
    """Processa cada domínio mostrando apenas resultados relevantes"""
    domain = domain.strip()
    if not domain:
        return
    
    clean_domain = domain.replace('*.', '')
    if not resolve_dns(clean_domain):
        print(f"{RED}[×] DNS não resolve: {clean_domain}{RESET}")
        return
    
    # Tentamos HTTPS primeiro, depois HTTP como fallback
    for scheme in ['https://', 'http://']:
        url = scheme + clean_domain
        if not check_url(url):
            continue
            
        theme = find_theme(url)
        if not theme:
            continue
            
        print(f"{GREEN}[+] Tema detectado: {theme} em {url}{RESET}")
        
        vulnerable, vuln_url = scan_git(url, theme)
        if vulnerable:
            print(f"{GREEN}[✔] VULNERÁVEL: {vuln_url}{RESET}")
            return vuln_url
        else:
            print(f"{RED}[×] .git não exposto para {theme}{RESET}")
    
    print(f"{RED}[×] Nenhuma vulnerabilidade encontrada em {domain}{RESET}")

def main():
    print(f"{BLUE}Git Exposure Scanner v1.5 - by chor4o{RESET}")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="URL única para verificar")
    parser.add_argument("-f", "--file", help="Arquivo com domínios")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Threads paralelas")
    args = parser.parse_args()

    if args.url:
        process_domain(args.url)
    elif args.file:
        with open(args.file) as f:
            domains = [line.strip() for line in f if line.strip()]
        
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            executor.map(process_domain, domains)
    else:
        print(f"{RED}Forneça uma URL (-u) ou arquivo (-f){RESET}")

if __name__ == "__main__":
    main()
