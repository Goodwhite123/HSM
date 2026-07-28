import os
import sys
import pkcs11
from pkcs11 import ObjectClass, Mechanism

def obter_driver():
    caminhos = [
        # Linux (Ubuntu / Debian / Docker / Alpine)
        "/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so",
        "/usr/lib/softhsm/libsofthsm2.so",
        "/usr/local/lib/softhsm/libsofthsm2.so",
        
        # macOS (Apple Silicon / Intel)
        "/opt/homebrew/lib/softhsm/libsofthsm2.so",
        
        # Windows (Instalação padrão do SoftHSM2)
        r"C:\Program Files\SoftHSM2\lib\softhsm2.dll",
        r"C:\Program Files (x86)\SoftHSM2\lib\softhsm2.dll"
    ]
    for caminho in caminhos:
        if os.path.exists(caminho):
            return pkcs11.lib(caminho)
    print("[!] Erro: Biblioteca libsofthsm2 (ou softhsm2.dll) não foi encontrada no computador.")
    sys.exit(1)

if __name__ == "__main__":
    TOKEN_LABEL = "LinkedIn_Vault"
    USER_PIN = "1234"
    KEY_LABEL = "minha-chave-api-python"
    
    # 1. Cria um documento de transação no disco
    conteudo_documento = b'{"id_transacao": "TX-9988", "cliente": "Gabriel Saes", "valor": 15000.00, "status": "APROVADO"}'
    with open("documento.txt", "wb") as f:
        f.write(conteudo_documento)
    print("[+] Arquivo 'documento.txt' gerado com sucesso.")

    lib = obter_driver()
    token = lib.get_token(token_label=TOKEN_LABEL)

    with token.open(user_pin=USER_PIN, rw=True) as session:
        try:
            # Pega apenas o PONTEIRO (handle) da chave privada lá dentro
            priv_key = session.get_key(label=KEY_LABEL, object_class=ObjectClass.PRIVATE_KEY)
        except pkcs11.exceptions.NoSuchKey:
            print(f"[!] Erro: Chave '{KEY_LABEL}' não encontrada. Rode o script 1_criar_chave.py primeiro!")
            sys.exit(1)

        print("[*] Enviando o hash do documento para processamento criptográfico no HSM...")
        
        assinatura_bytes = priv_key.sign(conteudo_documento, mechanism=Mechanism.SHA256_RSA_PKCS)
        
        with open("documento.sig", "wb") as f:
            f.write(assinatura_bytes)
            
        print(f"[✔] SUCESSO: Documento assinado! Assinatura salva em 'documento.sig' ({len(assinatura_bytes)} bytes).")