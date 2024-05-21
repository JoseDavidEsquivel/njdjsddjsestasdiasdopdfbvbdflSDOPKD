import hashlib
import os
import base64


contrasena = 'ELDIABO'

def generar_contrasena_salt (contrasena=contrasena):
    salt = os.urandom(16)  # Salt de 16 bytes (128 bits)
    # Concatenar el salt con la contraseña original
    contrasena_con_salt = salt + contrasena.encode('utf-8')

    # Crear un hash SHA-256 de la contraseña con salt
    sha256_hash = hashlib.sha256(contrasena_con_salt).digest()

    # Codificar el hash resultante en Base64
    contrasena_hashed_base64 = base64.b64encode(sha256_hash).decode('utf-8')
    print(salt)
    salt_base64 = base64.b64encode(salt).decode('utf-8')
    
    return salt_base64

print(generar_contrasena_salt(contrasena))
salt_base64=generar_contrasena_salt((contrasena))

salt_original = base64.b64decode(salt_base64.encode('utf-8'))
print(salt_base64)
print(salt_original)


