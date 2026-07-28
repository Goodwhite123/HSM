import os
import sys
import pkcs11
from pkcs11 import KeyType, ObjectClass, Attribute

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

    lib = obter_driver()
    
    try:
        token = lib.get_token(token_label=TOKEN_LABEL)
    except pkcs11.exceptions.NoSuchToken:
        print(f"[!] Erro: O token '{TOKEN_LABEL}' não existe. Rode o comando softhsm2-util --init-token primeiro.")
        sys.exit(1)

    print(f"[*] Conectando ao cofre '{TOKEN_LABEL}' para cerimônia de chaves...")
    
    with token.open(user_pin=USER_PIN, rw=True) as session:
        try:
            # Verifica se a chave já não foi criada antes
            session.get_key(label=KEY_LABEL, object_class=ObjectClass.PRIVATE_KEY)
            print(f"[!] A chave '{KEY_LABEL}' já existe no cofre! Nenhuma ação necessária.")
        except pkcs11.exceptions.NoSuchKey:
            print(f"[*] Gerando novo par RSA-2048 dentro do HSM...")
            pub_key, priv_key = session.generate_keypair(
                KeyType.RSA, 
                2048,
                label=KEY_LABEL,
                store=True,
                private_template={
                    Attribute.SIGN: True,
                    Attribute.EXTRACTABLE: False # GARANTE QUE A CHAVE NUNCA SAIA DO COFRE
                },
                public_template={
                    Attribute.VERIFY: True
                }
            )
            print(f"[✔] SUCESSO: Par de chaves '{KEY_LABEL}' gerado e lacrado no HSM!")