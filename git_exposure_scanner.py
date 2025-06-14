#!/usr/bin/env python3
"""
Git Exposure Scanner v1.4 - by chor4o
Versão com:
- Verificação DNS prévia
- Timeout ajustável
- Fallback para HTTP
- Verificação mais agressiva
"""

import requests
import socket
import argparse
import re
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurações
TIMEOUT = 5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
        requests.head(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
        return True
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
        f"/themes/{theme}/.git/"
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
                    if (git_file == "HEAD" and "ref:" in response.text) or \
                       (git_file == "config" and "[core]" in response.text):
                        return True, target_url
            except:
                continue
    return False, None

def process_domain(domain):
    """Processa cada domínio"""
    domain = domain.strip()
    if not domain:
        return
    
    print(f"\n{BLUE}[•] Verificando: {domain}{RESET}")
    
    # Verificação DNS
    clean_domain = domain.replace('*.', '')
    if not resolve_dns(clean_domain):
        print(f"{RED}[×] DNS não resolve: {clean_domain}{RESET}")
        return
    
    # Normalização e tentativa HTTPS/HTTP
    for scheme in ['https://', 'http://']:
        url = scheme + clean_domain
        if not check_url(url):
            continue
            
        print(f"{YELLOW}[→] Acessando: {url}{RESET}")
        
        # Detecção de tema
        theme = find_theme(url)
        if not theme:
            print(f"{YELLOW}[?] Tema não detectado{RESET}")
            continue
            
        print(f"{GREEN}[+] Tema detectado: {theme}{RESET}")
        
        # Varredura .git
        vulnerable, vuln_url = scan_git(url, theme)
        if vulnerable:
            print(f"{GREEN}[✔] VULNERÁVEL: {vuln_url}{RESET}")
            return vuln_url
        else:
            print(f"{RED}[×] .git não exposto{RESET}")
    
    print(f"{RED}[×] Nenhuma vulnerabilidade encontrada{RESET}")

def main():
    print(f"{BLUE}Git Exposure Scanner v1.4 - by chor4o{RESET}")
    
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
