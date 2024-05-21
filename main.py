from fastapi import FastAPI, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector

# Librerias para imagenes
from PIL import Image
import shutil

# Librerias para hashing y slat de contraseñas
import hashlib
import base64
import os

app = FastAPI()

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'presidencia'
}

# Modelo de datos
class Usuario(BaseModel):
    nombre: str
    contrasena: str
    estado: int
    permisos: int
    # salt: Optional[str] = None

class Credenciales(BaseModel):
    nombre: str
    contrasena: str

# funciones extra
def generar_contrasena_salt (contrasena):

    # Salt de 16 bytes (128 bits)
    salt = os.urandom(16)  
    # Salt en Base64 para guardar en la base de datos
    salt_base64 = base64.b64encode(salt).decode('utf-8')

    # Concatenar el salt con la contraseña original
    contrasena_con_salt = salt + contrasena.encode('utf-8')
    # Crear un hash SHA-256 de la contraseña con salt
    sha256_hash = hashlib.sha256(contrasena_con_salt).digest()
    # Codificar el hash resultante en Base64
    contrasena_hashed_base64 = base64.b64encode(sha256_hash).decode('utf-8')
    
    return (contrasena_hashed_base64,salt_base64)

# Función para verificar las credenciales
def verificar_credenciales(nombre: str, contrasena: str) -> bool:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT contrasena, salt FROM usuarios WHERE nombre = %s;"
        cursor.execute(query, (nombre,))
        usuario = cursor.fetchone()

        if usuario:

            contrasena_db, salt_base64 = usuario[0], usuario[1]
            salt_original = base64.b64decode(salt_base64.encode('utf-8'))

            # Generar hash SHA-256 de la contraseña proporcionada con el salt de la base de datos
            contrasena_con_salt = salt_original + contrasena.encode('utf-8')
            sha256_hash = hashlib.sha256(contrasena_con_salt).digest()
            contrasena_hashed = base64.b64encode(sha256_hash).decode('utf-8')
            # Comparar las contraseñas hasheadas
            if contrasena_hashed == contrasena_db:
                return True
            else:
                return False
        else:
            return False
    except mysql.connector.Error as err:
        print(f"Error al verificar credenciales en la base de datos: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

# Endpoint raiz
@app.get("/", status_code=status.HTTP_200_OK, summary="Endpoint raiz", tags=['Root'])
def root():
    return {'root'}

# Endpoint para iniciar sesión
@app.post("/login", status_code=status.HTTP_200_OK, summary="Endpoint para iniciar sesión", tags=['Login'])
def iniciar_sesion(credenciales: Credenciales):
    if verificar_credenciales(credenciales.nombre, credenciales.contrasena):
        return {"mensaje": "Sesión iniciada"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")


# Para el modulo de Usuarios
# Listar todos los usuarios (sin la contraseña)
@app.get("/listar_usuarios", status_code=status.HTTP_200_OK, summary="Endpoint para listar datos de usuarios", tags=['Usuario'])
def listar_usuarios():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id_usuario, nombre, estado, permisos FROM usuarios")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id': row[0],
                    'nombre': row[1],
                    'estado': row[2],
                    'permisos': row[3]
                }
                respuesta.append(dato)
            print(respuesta)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay usuarios en la Base de datos")
    finally:
        cursor.close()
        connection.close()

# Detalle de un usuario
@app.get("/detalle_usuario/{id_usuario}",status_code=status.HTTP_200_OK, summary="Endpoint para listar un solo usuario", tags=['Usuario'])
def detalle_usuario(id_usuario: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM usuarios WHERE id_usuario = %s;"
        cursor.execute(query, (id_usuario,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id': row[0],
                    'nombre': row[1],
                    'contrasena':row[2],
                    'estado': row[3],
                    'permisos': row[4]
                }
                respuesta.append(dato)
            print(respuesta)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    finally:
        cursor.close()
        connection.close()

# Crear un usuario
@app.post("/crear_usuario", status_code=status.HTTP_201_CREATED, summary="Endpoint para crear un nuevo usuario", tags=['Usuario'])
def crear_usuario(usuario: Usuario):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Validar valores de estado y permisos
        if usuario.estado not in [0, 1]:
            raise HTTPException(status_code=400, detail="El valor de 'estado' debe ser '0' o '1'")
        if usuario.permisos not in [0, 1]:
            raise HTTPException(status_code=400, detail="El valor de 'permisos' debe ser '0' o '1'")
        
        usuario.estado = str(usuario.estado) # Convertimos a str el estado y permisos para que no tome como posicion el valor
        usuario.permisos = str(usuario.permisos) # si no como el valor representado}

        contrasena_hashed , salt = generar_contrasena_salt(usuario.contrasena)

        # Insertar nuevo usuario en la base de datos
        query = "INSERT INTO usuarios (nombre, contrasena, estado, permisos, salt) VALUES (%s, %s, %s, %s, %s)"
        usuario_data = (usuario.nombre, contrasena_hashed, usuario.estado, usuario.permisos, salt)
        cursor.execute(query, usuario_data)
        connection.commit()

        return {
            "nombre":usuario.nombre,
            "estado":usuario.estado,
            "permisos":usuario.permisos,
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar usuario en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear usuario")
    finally:
        cursor.close()
        connection.close()

# Editar un usuario
@app.put("/editar_usuario/{id_usuario}", status_code=status.HTTP_200_OK, summary="Endpoint para editar un usuario existente", tags=['Usuario'])
def editar_usuario(id_usuario: int, usuario: Usuario):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Validar valores de estado y permisos
        if usuario.estado not in [0, 1]:
            raise HTTPException(status_code=400, detail="El valor de 'estado' debe ser '0' o '1'")
        if usuario.permisos not in [0, 1]:
            raise HTTPException(status_code=400, detail="El valor de 'permisos' debe ser '0' o '1'")
        
        usuario.estado = str(usuario.estado) # Convertimos a str el estado y permisos para que no tome como posicion el valor
        usuario.permisos = str(usuario.permisos) # si no como el valor representado

        contrasena_hashed , salt = generar_contrasena_salt(usuario.contrasena)


        # Actualizar usuario en la base de datos
        query = """
            UPDATE usuarios
            SET nombre = %s, contrasena = %s, estado = %s, permisos = %s , salt = %s
            WHERE id_usuario = %s
        """
        usuario_data = (usuario.nombre, contrasena_hashed, usuario.estado, usuario.permisos,salt, id_usuario)
        cursor.execute(query, usuario_data)
        connection.commit()

        # # Verificar si se actualizó algún registro
        # if cursor.rowcount == 0:
        #     raise HTTPException(status_code=404, detail=f"Usuario con id {id_usuario} no encontrado")

        return {"mensaje": f"Usuario con id {id_usuario} actualizado correctamente"}
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar usuario en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al editar usuario")
    finally:
        cursor.close()
        connection.close()

# Detalle de un usuario
@app.delete("/borrar_usuario/{id_usuario}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un usuario", tags=['Usuario'])
def borrar_usuario(id_usuario: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "DELETE FROM usuarios WHERE id_usuario = %s;"
        cursor.execute(query, (id_usuario,))
        connection.commit()  # Es importante hacer commit después de un DELETE en la base de datos

        if cursor.rowcount > 0:
            return {"mensaje": f"Usuario con id {id_usuario} eliminado correctamente"}
        else:
            raise HTTPException(status_code=404, detail=f"Usuario con id {id_usuario} no encontrado")
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al borrar usuario en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al borrar usuario")
    finally:
        cursor.close()
        connection.close()


@app.get("/listar_logo",status_code=status.HTTP_200_OK, summary="Endpoint para listar el logo activo de la pagina", tags=['Logo'])
def listar_logo():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM logo")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id': row[0],
                    'nombre': row[1],
                    'estado': row[2],
                    'permisos': row[3]
                }
                respuesta.append(dato)
            print(respuesta)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No un logo en la Base de datos")
    finally:
        cursor.close()
        connection.close()


@app.post("/subir_logo",status_code=status.HTTP_200_OK, summary="Endpoint para subir un logo a la pagina", tags=['Logo'])
async def subir_logo(file: UploadFile = File(...)):
    # Comprobar la extensión del archivo
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    if not file.filename.lower().endswith(".png"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos con extension .png")

    # Guardar temporalmente el archivo
    file_location = f"static/temp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Abrir la imagen y comprobar el tamaño
    try:
        with Image.open(file_location) as img:
            if img.size < (200, 200):
                raise HTTPException(status_code=400, detail="El logo tiene que ser mayor a 200x200")
            elif img.size > (500, 500):
                raise HTTPException(status_code=400, detail="El logo tiene que ser menor a 500x500")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Mover el archivo al directorio final si pasa las validaciones
    final_location = f"static/images/logos/{file.filename}" # Ubicacion del archivo
    shutil.move(file_location, final_location)

    query = """
            UPDATE logo
            SET imagen = %s, ruta = %s
            WHERE id_logo = 1
        """
    usuario_data = (file.filename,"static/images/logos/")
    cursor.execute(query, usuario_data)
    connection.commit()

    return JSONResponse(content={"filename": file.filename})
