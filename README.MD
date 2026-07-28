# 🛡️ Enterprise HSM (Hardware Security Module) Home Lab

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Security Protocol](https://img.shields.io/badge/Security-PKCS%2311-green?style=for-the-badge&logo=protonvpn&logoColor=white)
![Vault Technology](https://img.shields.io/badge/Vault-SoftHSMv2-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge)

> **Projeto prático de arquitetura de segurança simulando o ciclo de vida e a gestão de chaves em um Hardware Security Module (HSM) corporativo via padrão industrial PKCS#11 em Python.**

---

## 📌 Visão Geral & Problema de Cibersegurança

Armazenar chaves privadas de criptografia em arquivos de configuração (`.env`), banco de dados ou variáveis de ambiente expõe aplicações a ataques de exfiltração de dados em memória ou vazamento de código fonte.

### A Solução por HSM
Em infraestruturas bancárias, Open Finance e PKI corporativas, o **HSM (Hardware Security Module)** é utilizado para isolar o ciclo de vida das chaves:
1. **Chaves Não Extraíveis (`EXTRACTABLE = False`)**: A chave privada é gerada dentro do cofre e **jamais exposta em texto plano**.
2. **Offloading Criptográfico**: A aplicação Python não lê a chave; ela envia o payload via protocolo **PKCS#11**, o HSM assina/processa os dados internamente e retorna apenas a assinatura digital.

---

## 🏗️ Arquitetura do Laboratório

O laboratório é desacoplado em **3 scripts independentes**, simulando a separação de responsabilidades em uma arquitetura de microsserviços:

```text
┌────────────────────────┐      ┌───────────────────────────┐      ┌─────────────────────────────┐
│   1_criar_chave.py     │ ───► │  2_assinar_documento.py   │ ───► │ 3_verificar_assinatura.py   │
└────────────────────────┘      └───────────────────────────┘      └─────────────────────────────┘
  Cerimônia de Chaves             Gera 'documento.txt'               Validação e Auditoria
  (RSA-2048 com                   e obtém a assinatura               via Chave Pública no
   EXTRACTABLE: False)            'documento.sig' via HSM            cofre criptográfico

   1_criar_chave.py → Inicializa um par de chaves RSA-2048 no HSM com EXTRACTABLE=False.

   2_assinar_documento.py → Cria documento.txt, envia ao HSM e gera documento.sig.

   3_verificar_assinatura.py → Valida se o documento corresponde à assinatura e não foi adulterado.


    ⚙️ Instalação e Configuração

        git clone https://github.com/Goodwhite123/HSM.git
        cd HSM


    🧩 Configurar Ambiente Virtual

        python3 -m venv venv
        source venv/bin/activate
        pip install python-pkcs11


        No Windows PowerShell:

        .\venv\Scripts\Activate.ps1


    🧱 Instalar o SoftHSM2

        sudo apt-get update && sudo apt-get install -y softhsm2


    macOS (Homebrew):

        brew install softhsm

    Windows (Chocolatey):

        choco install softhsm


    🔑 Inicializar o Token

        mkdir -p ~/.config/softhsm2/tokens

        cat <<EOF> ~/.config/softhsm2/softhsm2.conf
        directories.tokendir = $HOME/.config/softhsm2/tokens
        objectstore.backend = file
        EOF

        export SOFTHSM2_CONF=$HOME/.config/softhsm2/softhsm2.conf

        softhsm2-util --init-token --slot 0 --label "LinkedIn_Vault" --so-pin 123456 --pin 1234


    ▶️ Execução
        bash

        # 1. Gera o par de chaves no cofre
        python3 1_criar_chave.py

        # 2. Cria o arquivo e gera a assinatura
        python3 2_assinar_documento.py

        # 3. Verifica a autenticidade
        python3 3_verificar_assinatura.py
