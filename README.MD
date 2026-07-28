Markdown

# 🛡️ Enterprise HSM (Hardware Security Module) Home Lab

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Security Protocol](https://img.shields.io/badge/Security-PKCS%2311-green?style=for-the-badge&logo=protonvpn&logoColor=white)
![Vault Technology](https://img.shields.io/badge/Vault-SoftHSMv2-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge)

> **Projeto prático de arquitetura de segurança simulando o ciclo de vida completo e a gestão de chaves em um Hardware Security Module (HSM) corporativo via padrão industrial PKCS#11 em Python.**

---

## 📌 Visão Geral & Problema de Cibersegurança

Armazenar chaves privadas de criptografia em arquivos de configuração (`.env`), banco de dados ou variáveis de ambiente expõe aplicações a ataques de exfiltração de dados em memória RAM ou vazamento de código fonte.

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

📥 Guia Completo: Do Clone à Execução

Siga este passo a passo para rodar o projeto do zero em qualquer máquina.
1. Clonar o Repositório

Abra o seu terminal e rode:
Bash

git clone [https://github.com/Goodwhite123/HSM.git](https://github.com/Goodwhite123/HSM.git)
cd HSM

2. Preparar o Ambiente Virtual Python (venv)

Crie um ambiente virtual para isolar as dependências e instale a biblioteca de comunicação PKCS#11:
Bash

# Cria o ambiente virtual
python3 -m venv venv

# Ativa o ambiente virtual no Linux/macOS
source venv/bin/activate

# (Opcional) No Windows PowerShell, ative com:
# .\venv\Scripts\Activate.ps1

# Instala a dependência do laboratório
pip install python-pkcs11

3. Instalar o Motor do SoftHSM2 no Sistema Operacional

O SoftHSM2 é o emulador de HSM nativo que processará as operações de hardware.

    🐧 Linux (Ubuntu / Debian / Mint):
    Bash

    sudo apt-get update && sudo apt-get install -y softhsm2

    🍎 macOS (Homebrew):
    Bash

    brew install softhsm

    🪟 Windows:
    Baixe o instalador oficial .msi do SoftHSM2 no GitHub oficial do OpenDNSSEC ou use o gerenciador Chocolatey:
    PowerShell

    choco install softhsm

4. Configurar e Inicializar o Cofre Criptográfico (Slot PKCS#11)

Antes de rodar os scripts, crie o cofre local rodando os comandos abaixo no seu terminal:
Bash

# 1. Cria a pasta oculta para armazenar os tokens
mkdir -p ~/.config/softhsm2/tokens

# 2. Gera o arquivo de configuração do SoftHSM
cat <<EOF> ~/.config/softhsm2/softhsm2.conf
directories.tokendir = $HOME/.config/softhsm2/tokens
objectstore.backend = file
EOF

# 3. Informa ao sistema o caminho da configuração
export SOFTHSM2_CONF=$HOME/.config/softhsm2/softhsm2.conf

# 4. Inicializa o token com o rótulo "LinkedIn_Vault", PIN de usuário "1234" e SO-PIN "123456"
softhsm2-util --init-token --slot 0 --label "LinkedIn_Vault" --so-pin 123456 --pin 1234

    💡 Dica: Para não precisar digitar o comando export toda vez que abrir o terminal, adicione ao seu bash:
    Bash

    echo 'export SOFTHSM2_CONF=$HOME/.config/softhsm2/softhsm2.conf' >> ~/.bashrc

🚀 Executando o Fluxo do Laboratório

Com o ambiente pronto e o cofre inicializado, rode os scripts na ordem numérica:
Bash

# Passo 1: Cerimônia de Chaves (Gera e sela a chave privada RSA no HSM)
python3 1_criar_chave.py

# Passo 2: Aplicação (Gera 'documento.txt' e solicita a assinatura 'documento.sig')
python3 2_assinar_documento.py

# Passo 3: Auditoria (Confecciona a verificação do documento e da assinatura via HSM)
python3 3_verificar_assinatura.py

🧪 Provando a Integridade (Simulação de Ataque Hacker)

Para demonstrar o funcionamento do HSM em uma auditoria de segurança:

    Adultere o arquivo original via terminal (simulando um hacker alterando o valor da transação de R$ 15.000 para R$ 95.000):
    Bash

    sed -i 's/15000.00/95000.00/g' documento.txt

    Execute o script de verificação novamente:
    Bash

    python3 3_verificar_assinatura.py

    Resultado: O motor do HSM rejeita a assinatura imediatamente com um alerta de FALHA DE SEGURANÇA, provando que o payload foi alterado após a emissão.

🚨 Guia de Troubleshooting (Se Der "Merda", Resolva Aqui!)

Caso encontre algum erro durante a execução, consulte as soluções abaixo:
1. Erro: externally-managed-environment ao rodar pip install

    Causa: Seu sistema operacional bloqueia instalações globais do pip.

    Solução: Crie e ative um ambiente virtual (python3 -m venv venv && source venv/bin/activate) ou force com:
    Bash

    pip install python-pkcs11 --break-system-packages

2. Erro: ERROR: Could not load the SoftHSM configuration ou pkcs11.exceptions.GeneralError

    Causa: O SoftHSM não encontrou o arquivo de configuração softhsm2.conf.

    Solução: Re-exporte a variável de ambiente apontando para a sua configuração local:
    Bash

    export SOFTHSM2_CONF=$HOME/.config/softhsm2/softhsm2.conf

3. Erro: [!] ERRO FATAL: Biblioteca nativa do SoftHSM2 não encontrada no sistema.

    Causa: O driver .so ou .dll do PKCS#11 está em uma pasta diferente.

    Solução: Localize o arquivo no seu sistema e passe o caminho via variável de ambiente:
    Bash

    # No Linux, encontre o caminho:
    find /usr -name "libsofthsm2.so" 2>/dev/null

    # Defina a variável antes de rodar o Python:
    export PKCS11_MODULE_PATH="/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so"

4. Erro: TypeError: get_tokens() got an unexpected keyword argument 'label'

    Causa: Uso de parâmetro descontinuado da biblioteca.

    Solução: Verifique se o seu código usa o argumento nomeado token_label=:
    Python

    token = self.lib.get_token(token_label="LinkedIn_Vault")

5. Erro: TypeError: unsupported operand type(s) for &: 'MechanismFlag' and 'dict'

    Causa: Passar o dicionário no parâmetro capabilities={...} no método generate_keypair().

    Solução: Utilize a sintaxe moderna com private_template e public_template:
    Python

    pub_key, priv_key = session.generate_keypair(
        KeyType.RSA, 2048, label=key_label, store=True,
        private_template={Attribute.SIGN: True, Attribute.EXTRACTABLE: False},
        public_template={Attribute.VERIFY: True}
    )