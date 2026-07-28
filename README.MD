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