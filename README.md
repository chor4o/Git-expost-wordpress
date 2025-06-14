# Git Exposure Scanner

Scanner avançado para detectar diretórios `.git` expostos em sites WordPress e outros sistemas web.

![GitHub](https://img.shields.io/github/license/seu-usuario/git-exposure-scanner)
![Python](https://img.shields.io/badge/Python-3.x-blue)

## 📌 Funcionalidades

- ✅ Detecção automática de temas WordPress
- 🔍 Varredura agressiva por `.git` exposto
- 🌐 Suporte a wildcards (ex: `*.dominio.com`)
- 🔄 Fallback automático HTTP/HTTPS
- 🚀 Multi-threading para varredura rápida
- 📊 Saída colorida e organizada

## 🛠 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/git-exposure-scanner.git
cd git-exposure-scanner

Instale as dependências:
pip install -r requirements.txt

🚀 Como Usar
Verificar um único domínio:

python git_exposure_scanner.py -u exemplo.com
Verificar múltiplos domínios (arquivo):

python git_exposure_scanner.py -f lista_dominios.txt -t 10
Opções:
text
-u, --url        URL única para verificar
-f, --file       Arquivo com lista de domínios (um por linha)
-t, --threads    Número de threads paralelas (padrão: 5)
📝 Exemplo de Saída
text
[•] Verificando: exemplo.com
[→] Acessando: https://exemplo.com
[+] Tema detectado: astra
[✔] VULNERÁVEL: https://exemplo.com/wp-content/themes/astra/.git/config
🛡 Casos de Uso Ético
Testes de penetração autorizados

Bug bounty

Auditorias de segurança web

📄 Licença
MIT License - Consulte o arquivo LICENSE para detalhes.

Feito com ❤️ por chor4o - Contribuições são bem-vindas!
