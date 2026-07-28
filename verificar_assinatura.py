import os
import sys
import pkcs11
from pkcs11 import ObjectClass, Mechanism

def obter_driver():
    caminhos = [
        "/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so", # Linux / Docker
        "/usr/lib/softhsm/libsofthsm2.so",                  # Alpine / RHEL
        "/usr/local/lib/softhsm/libsofthsm2.so",            # Custom Linux
        "/opt/homebrew/lib/softhsm/libsofthsm2.so",         # macOS
        r"C:\Program Files\SoftHSM2\lib\softhsm2.dll",      # Windows 64-bit
        r"C:\Program Files (x86)\SoftHSM2\lib\softhsm2.dll" # Windows 32-bit
    ]
    for caminho in caminhos:
        if os.path.exists(caminho):
            return pkcs11.lib(caminho)
    print("[!] ERRO FATAL: Biblioteca nativa do SoftHSM2 não encontrada no sistema.")
    sys.exit(1)

if __name__ == "__main__":
    TOKEN_LABEL = "LinkedIn_Vault"
    USER_PIN = "1234"
    KEY_LABEL = "minha-chave-api-python"

    print("==========================================================")
    print("  🛡️  SISTEMA DE AUDITORIA E VERIFICAÇÃO VIA HSM (PKCS#11)")
    print("==========================================================")

    # -------------------------------------------------------------------------
    # TRATATIVA PROFISSIONAL DE LEITURA DE ARQUIVOS (Padrão EAFP)
    # -------------------------------------------------------------------------
    try:
        print("[*] Carregando documento original e assinatura criptográfica do disco...")
        
        with open("documento.txt", "rb") as f_doc:
            dados_originais = f_doc.read()
            
        with open("documento.sig", "rb") as f_sig:
            assinatura_recebida = f_sig.read()

        print(f"[+] Arquivos carregados! Payload: {len(dados_originais)} bytes | Assinatura: {len(assinatura_recebida)} bytes.")

    except FileNotFoundError as e:
        print(f"\n[✘] FALHA DE PRÉ-REQUISITO: O arquivo '{e.filename}' não foi encontrado.")
        print("    -> DICA: Execute o script '2_assinar_documento.py' primeiro para gerar a transação e a assinatura.")
        sys.exit(1)
        
    except PermissionError as e:
        print(f"\n[✘] ERRO DE PERMISSÃO: O sistema operacional negou leitura ao arquivo '{e.filename}'.")
        print("    -> DICA: Verifique as permissões de acesso da pasta atual ou rode com o usuário correto.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n[✘] ERRO INESPERADO ao tentar ler os artefatos em disco: {str(e)}")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # CONEXÃO COM O COFRE E AUDITORIA CRIPTOGRÁFICA
    # -------------------------------------------------------------------------
    print(f"[*] Conteúdo inspecionado: {dados_originais.decode('utf-8')}")

    lib = obter_driver()
    
    try:
        token = lib.get_token(token_label=TOKEN_LABEL)
    except pkcs11.exceptions.NoSuchToken:
        print(f"[!] Erro: O cofre '{TOKEN_LABEL}' não foi encontrado no HSM.")
        sys.exit(1)

    with token.open(user_pin=USER_PIN, rw=True) as session:
        try:
            # Para verificar uma assinatura, o padrão exige apenas a Chave Pública
            pub_key = session.get_key(label=KEY_LABEL, object_class=ObjectClass.PUBLIC_KEY)
        except pkcs11.exceptions.NoSuchKey:
            print(f"[!] Erro: A chave pública '{KEY_LABEL}' não está registrada neste cofre.")
            print("    -> DICA: Execute o script '1_criar_chave.py' para realizar a cerimônia de chaves.")
            sys.exit(1)

        print("[*] Enviando payload e assinatura para processamento matemático no HSM...")
        
        try:
            # A computação de verificação acontece de forma isolada via motor PKCS#11
            é_autentico = pub_key.verify(dados_originais, assinatura_recebida, mechanism=Mechanism.SHA256_RSA_PKCS)
            
            print("-" * 60)
            if é_autentico:
                print("[✔] RESULTADO: ASSINATURA VÁLIDA E AUTÊNTICA!")
                print("    Integridade confirmada: O documento não foi alterado e foi emitido por este cofre.")
            else:
                print("[✘] RESULTADO: ALERTA DE SEGURANÇA! A assinatura é INVÁLIDA.")
            print("-" * 60)
            
        except pkcs11.exceptions.SignatureInvalid:
            # Algumas implementações do PKCS#11 lançam exceção quando a assinatura é falsa
            print("-" * 60)
            print("[✘] RESULTADO: ALERTA DE SEGURANÇA! Assinatura rejeitada pelo motor criptográfico.")
            print("    O arquivo 'documento.txt' foi adulterado ou a chave foi comprometida!")
            print("-" * 60)