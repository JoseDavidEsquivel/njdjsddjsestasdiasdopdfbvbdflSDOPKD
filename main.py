from fastapi import FastAPI, HTTPException, status, File, UploadFile, Form, Path, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from datetime import date, time
from typing import Optional, List
import mysql.connector
import jwt
import datetime

# Librerias para imagenes
from PIL import Image
import shutil

# Librerias para hashing y slat de contraseñas
import hashlib
import base64
import os

app = FastAPI()

# Configuración de la base de datos si esta en la nube 
# db_config = {
#     'host': '151.106.97.153',
#     'user': 'u880599588_test',
#     'password': 'HCwf9J9a',
#     'database': 'u880599588_test'
# }
# Configuracion de la base de datos si esta de forma local
db_config ={    
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'presidencia'
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos
class Usuario(BaseModel):
    nombre: str
    contrasena: str
    area: str
    estado: int
    permisos: int
    # salt: Optional[str] = None

class Credenciales(BaseModel):
    nombre: str
    contrasena: str

class Carrusel(BaseModel):
    estado: int
    url: str

class Ubicaciones(BaseModel):
    latitud: float
    longitud: float
    lugar: str

class Contacto(BaseModel):
    nombre_institucion: str
    tipo_contacto: str
    contacto: str
    horario: str

class Evento(BaseModel):
    titulo: str
    descripcion: str
    fecha: date
    hora: time

class Bot(BaseModel):
    nombre: str
    correo: str
    problema: str
    area: str

class Encuestas(BaseModel):
    titulo: str

class Preguntas(BaseModel):
    id_encuesta: int
    pregunta: str
    pregunta_abierta: int
    pregunta_cerrada_multiple: int

class EditarPregunta(BaseModel):
    pregunta:str

class Opciones(BaseModel):
    id_pregunta:int
    id_encuesta: int
    opcion: str

class EditarOpcion(BaseModel):
    opcion: str

class Respuesta_abierta(BaseModel):
    id_pregunta:int
    id_encuesta: int
    respuesta: str

class Editar_respuesta_abierta(BaseModel):
    respuesta: str

class Respuesta_cerrada(BaseModel):
    id_opcion: int
    id_pregunta:int
    id_encuesta: int

class Editar_respuesta_cerrada(BaseModel):
    id_opcion: int

class Articulo(BaseModel):
    num_articulo: int

class Fraccion(BaseModel):
    fraccion: str
    descripcion: str
    area: str
    num_articulo: int

class Año(BaseModel):
    año: int
    id_fraccion: int

class Trimestre(BaseModel):
    trimestre: int
    id_año: int

class Documento(BaseModel):
    id_trimestre: int
    documento: str

class Tramite(BaseModel):
    nombre: str

class Requisito(BaseModel):
    requisito: str
    id_tramite: int

class Editar_requisito(BaseModel):
    requisito: str

class Color(BaseModel):
    nombre_color: str
    valor_hex: str

app.mount("/static", StaticFiles(directory="static"),name="static")

# Endpoint raiz
@app.get("/", status_code=status.HTTP_200_OK, summary="Endpoint raiz", tags=['Root'])
def root():
    return {'root'}

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
def verificar_credenciales(nombre: str, contrasena: str):
    # Clave secreta para firmar los tokens JWT
    SECRET_KEY = "MEXICO_0-4_URUGUAY" # MAFUFADA DE SELECCION

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT contrasena, salt, permisos, estado, area FROM usuarios WHERE nombre = %s;"
        cursor.execute(query, (nombre,))
        usuario = cursor.fetchone()

        if usuario:
            contrasena_db, salt_base64 = usuario[0], usuario[1]
            salt_original = base64.b64decode(salt_base64.encode('utf-8'))

            # Generar hash SHA-256 de la contraseña proporcionada con el salt de la base de datos
            contrasena_con_salt = salt_original + contrasena.encode('utf-8')
            sha256_hash = hashlib.sha256(contrasena_con_salt).digest()
            contrasena_hashed = base64.b64encode(sha256_hash).decode('utf-8')

            if contrasena_hashed == contrasena_db:
                estado = usuario[3]
                if estado == '0':
                    return {"mensaje": "Usuario no activo"}
                else:
                    nivel_permiso = usuario[2]
                    area = usuario[4]
                    if nivel_permiso == '0':
                        rol = 'director transparencia'
                    elif nivel_permiso == '1':
                        rol = 'administrador'
                    else:
                        rol = 'director area'
                    
                    # Generar el token JWT
                    token = jwt.encode({
                        'nombre': nombre,
                        'rol': rol,
                        'area': area,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                    }, SECRET_KEY, algorithm='HS256')

                    return {"mensaje": "Credenciales correctas", "rol": rol, "area": area, "token": token}
            else:
                return {"mensaje": "Credenciales incorrectas"}
        else:
            return {"mensaje": "Credenciales incorrectas"}
    except mysql.connector.Error as err:
        print(f"Error al verificar credenciales en la base de datos: {err}")
        return {"mensaje": "Error al verificar credenciales en la base de datos"}
    finally:
        cursor.close()
        connection.close()

# Endpoint para iniciar sesión
@app.post("/login", status_code=status.HTTP_200_OK, summary="Endpoint para iniciar sesión", tags=['Login'])
def iniciar_sesion(credenciales: Credenciales):
    resultado_verificacion = verificar_credenciales(credenciales.nombre, credenciales.contrasena)

    if resultado_verificacion["mensaje"] == "Credenciales correctas":
        return {
            "mensaje": "Sesión iniciada",
            "rol": resultado_verificacion["rol"],
            "area": resultado_verificacion["area"],
            "token": resultado_verificacion["token"]
        }
    elif resultado_verificacion["mensaje"] == "Usuario no activo":
        raise HTTPException(status_code=403, detail="Usuario no activo")
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
# Para el modulo de Usuarios
# Listar todos los usuarios (sin la contraseña)
@app.get("/usuario", status_code=status.HTTP_200_OK, summary="Endpoint para listar datos de usuarios", tags=['Usuario'])
def listar_usuarios():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id_usuario, nombre, area, estado, permisos FROM usuarios")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id': row[0],
                    'nombre': row[1],
                    'area':row[2],
                    'estado': row[3],
                    'permisos': row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay usuarios en la Base de datos")
    finally:
        cursor.close()
        connection.close()

# Detalle de un usuario
@app.get("/usuario/{id_usuario}",status_code=status.HTTP_200_OK, summary="Endpoint para listar un solo usuario", tags=['Usuario'])
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
                    'area': row[3],
                    'estado': row[4],
                    'permisos': row[5]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    finally:
        cursor.close()
        connection.close()

# Crear un usuario
@app.post("/usuario/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un nuevo usuario", tags=['Usuario'])
def crear_usuario(usuario: Usuario):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Validar valores de estado y permisos
        if usuario.estado not in [0, 1]:
            raise HTTPException(status_code=400, detail="El valor de 'estado' debe ser '0', '1'")
        if usuario.permisos not in [0, 1, 2]:
            raise HTTPException(status_code=400, detail="El valor de 'permisos' debe ser '0', '1' o '2'")
        
        usuario.estado = str(usuario.estado) # Convertimos a str el estado y permisos para que no tome como posicion el valor
        usuario.permisos = str(usuario.permisos) # si no como el valor representado}

        contrasena_hashed , salt = generar_contrasena_salt(usuario.contrasena)

        # Insertar nuevo usuario en la base de datos
        query = "INSERT INTO usuarios (nombre, contrasena, area, estado, permisos, salt) VALUES (%s, %s, %s, %s, %s,%s)"
        usuario_data = (usuario.nombre, contrasena_hashed, usuario.area, usuario.estado, usuario.permisos, salt)
        cursor.execute(query, usuario_data)
        connection.commit()

        return {
            "nombre":usuario.nombre,
            "area": usuario.area,
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
@app.put("/usuario/editar/{id_usuario}", status_code=status.HTTP_200_OK, summary="Endpoint para editar un usuario existente", tags=['Usuario'])
def editar_usuario(id_usuario: int, usuario: Usuario):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Validar valores de estado y permisos
        if usuario.estado not in [0, 1]:
            raise HTTPException(status_code=400, detail="El valor de 'estado' debe ser '0' o '1'")
        if usuario.permisos not in [0, 1, 2]:
            raise HTTPException(status_code=400, detail="El valor de 'permisos' debe ser '0', '1' o '2'")
        
        usuario.estado = str(usuario.estado) # Convertimos a str el estado y permisos para que no tome como posicion el valor
        usuario.permisos = str(usuario.permisos) # si no como el valor representado

        # Obtener la contraseña y el salt actuales de la base de datos
        cursor.execute("SELECT contrasena, salt FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail=f"Usuario con id {id_usuario} no encontrado")
        
        contrasena_actual_hashed, salt_actual = resultado

        # Verificar si la contraseña proporcionada es la misma que la almacenada
        if usuario.contrasena == contrasena_actual_hashed:
            contrasena_hashed, salt = contrasena_actual_hashed, salt_actual
        else:
            contrasena_hashed, salt = generar_contrasena_salt(usuario.contrasena)

        # Actualizar usuario en la base de datos
        query = """
            UPDATE usuarios
            SET nombre = %s, contrasena = %s, area = %s, estado = %s, permisos = %s , salt = %s
            WHERE id_usuario = %s
        """
        usuario_data = (usuario.nombre, contrasena_hashed, usuario.area, usuario.estado, usuario.permisos, salt, id_usuario)
        cursor.execute(query, usuario_data)
        connection.commit()

        return {"mensaje": f"Usuario con id {id_usuario} actualizado correctamente"}
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar usuario en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al editar usuario")
    finally:
        cursor.close()
        connection.close()

# Detalle de un usuario
@app.delete("/usuario/borrar/{id_usuario}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un usuario", tags=['Usuario'])
def borrar_usuario(id_usuario: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "DELETE FROM usuarios WHERE id_usuario = %s;"
        cursor.execute(query, (id_usuario,))
        connection.commit() 

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

@app.get("/logo",status_code=status.HTTP_200_OK, summary="Endpoint para listar el logo activo de la pagina", tags=['Logo'])
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
                    'archivo': row[1],
                    'ruta': row[2]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No un logo en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/logo/subir",status_code=status.HTTP_200_OK, summary="Endpoint para subir un logo a la pagina", tags=['Logo'])
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
            elif img.size > (1500, 1500):
                raise HTTPException(status_code=400, detail="El logo tiene que ser menor a 1500x1500")
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

@app.post("/logo/borrar", status_code=status.HTTP_200_OK, summary="Endpoint para borrar el logo actual", tags=['Logo'])
async def borrar_logo():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Obtener el nombre del archivo actual
    cursor.execute("SELECT imagen FROM logo WHERE id_logo = 1")
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Logo no encontrado")

    current_filename = result[0]
    default_filename = "default_icon.png"
    default_path = "static/images/logos/"

    # Actualizar la base de datos con el nombre del archivo por defecto
    query = """
            UPDATE logo
            SET imagen = %s, ruta = %s
            WHERE id_logo = 1
        """
    cursor.execute(query, (default_filename, default_path))
    connection.commit()

    # Borrar el archivo físico si no es el archivo por defecto
    if current_filename != default_filename:
        current_file_path = os.path.join(default_path, current_filename)
        if os.path.exists(current_file_path):
            os.remove(current_file_path)

    cursor.close()
    connection.close()

    return JSONResponse(content={"message": "Logo borrado y reemplazado por el ícono por defecto"})

# @app.get("/header",status_code=status.HTTP_200_OK, summary="Endpoint para listar el header activo de la pagina", tags=['Header'])
# def listar_header():
#     connection = mysql.connector.connect(**db_config)
#     cursor = connection.cursor()
#     try:
#         cursor.execute("SELECT * FROM header")
#         datos = cursor.fetchall()
#         if datos:
#             respuesta = []
#             for row in datos:
#                 dato = {
#                     'archivo': row[1],
#                     'ruta': row[2]
#                 }
#                 respuesta.append(dato)
            

#             return respuesta
#         else:
#             raise HTTPException(status_code=404, detail="No hay un header en la Base de datos")
#     finally:
#         cursor.close()
#         connection.close()

# @app.post("/header/subir",status_code=status.HTTP_200_OK, summary="Endpoint para subir un header a la pagina", tags=['Header'])
# async def subir_header(file: UploadFile = File(...)):
#     # Comprobar la extensión del archivo
#     connection = mysql.connector.connect(**db_config)
#     cursor = connection.cursor()

#     if not file.filename.lower().endswith(".png"):
#         raise HTTPException(status_code=400, detail="Solo se permiten archivos con extension .png")

#     # Guardar temporalmente el archivo
#     file_location = f"static/temp/{file.filename}"
#     with open(file_location, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Abrir la imagen y comprobar el tamaño
#     try:
#         with Image.open(file_location) as img:
#             if img.size < (200, 200):
#                 raise HTTPException(status_code=400, detail="El header tiene que ser mayor a 200x200")
#             elif img.size > (1500, 1500):
#                 raise HTTPException(status_code=400, detail="El header tiene que ser menor a 1500x1500")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Invalid image file")

#     # Mover el archivo al directorio final si pasa las validaciones
#     final_location = f"static/images/headers/{file.filename}" # Ubicacion del archivo
#     shutil.move(file_location, final_location)

#     query = """
#             UPDATE header
#             SET imagen = %s, ruta = %s
#             WHERE id_header = 1
#         """
#     usuario_data = (file.filename,"static/images/header/")
#     cursor.execute(query, usuario_data)
#     connection.commit()

#     return JSONResponse(content={"filename": file.filename})

# @app.post("/header/borrar", status_code=status.HTTP_200_OK, summary="Endpoint para borrar el header actual", tags=['Header'])
# async def borrar_header():
#     connection = mysql.connector.connect(**db_config)
#     cursor = connection.cursor()

#     # Obtener el nombre del archivo actual
#     cursor.execute("SELECT imagen FROM header WHERE id_header = 1")
#     result = cursor.fetchone()
#     if result is None:
#         raise HTTPException(status_code=404, detail="Header no encontrado")

#     current_filename = result[0]
#     default_filename = "default_header.png"
#     default_path = "static/images/header/"

#     # Actualizar la base de datos con el nombre del archivo por defecto
#     query = """
#             UPDATE header
#             SET imagen = %s, ruta = %s
#             WHERE id_header = 1
#         """
#     cursor.execute(query, (default_filename, default_path))
#     connection.commit()

#     # Borrar el archivo físico si no es el archivo por defecto
#     if current_filename != default_filename:
#         current_file_path = os.path.join(default_path, current_filename)
#         if os.path.exists(current_file_path):
#             os.remove(current_file_path)

#     cursor.close()
#     connection.close()

#     return JSONResponse(content={"message": "Header borrado y reemplazado por el header por defecto"})

@app.get("/avisos",status_code=status.HTTP_200_OK, summary="Endpoint para listar los avisos de la pagina", tags=['Carrusel'])
def listar_avisos():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM carrusel")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_aviso':row[0],
                    'imagen': row[1],
                    'ruta': row[2],
                    'estado': row[3],
                    'url': row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay avisos en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/avisos/activos",status_code=status.HTTP_200_OK, summary="Endpoint para listar los avisos de la pagina", tags=['Carrusel'])
def listar_avisos_activos():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM carrusel WHERE estado ='1'")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_aviso':row[0],
                    'imagen': row[1],
                    'ruta': row[2],
                    'estado': row[3],
                    'url': row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay avisos activos en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/aviso/{id_aviso}",status_code=status.HTTP_200_OK, summary="Endpoint para listar un aviso del carrusel de la pagina", tags=['Carrusel'])
def detalle_aviso(id_aviso:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM carrusel WHERE id_imagen= %s"
        cursor.execute(query, (id_aviso,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_aviso':row[0],
                    'imagen': row[1],
                    'ruta': row[2],
                    'estado': row[3],
                    'url': row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe ese aviso en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/aviso/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un aviso y que se vea reflejado en el carrusel de imágenes", tags=['Carrusel'])
async def crear_aviso(
    estado: int = Form(...),
    url: str = Form(...),
    file: UploadFile = File(...)
): 
    # Validar valores de estado y permisos
    if estado not in [0, 1]:
        raise HTTPException(status_code=400, detail="El valor de 'estado' debe ser '0' o '1'")
        
    estado = str(estado) # Convertimos a str el estado y permisos para que no tome como posicion el valor
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Guardar temporalmente el archivo
    file_location = f"static/temp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Abrir la imagen y comprobar el tamaño
    try:
        with Image.open(file_location) as img:
            if img.size < (200, 200):
                raise HTTPException(status_code=400, detail="La imagen tiene que ser mayor a 200x200")
            elif img.size > (1500, 1500):
                raise HTTPException(status_code=400, detail="La imagen tiene que ser menor a 1500x1500")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Mover el archivo al directorio final si pasa las validaciones
    final_location = f"static/images/carrusel/{file.filename}"
    shutil.move(file_location, final_location)

    # Insertar datos en la base de datos
    query = 'INSERT INTO carrusel (imagen, ruta, estado, url) VALUES (%s,%s,%s,%s)'
    usuario_data = (file.filename, "static/images/carrusel/", estado, url)
    cursor.execute(query, usuario_data)
    connection.commit()

    return JSONResponse(content={
        "filename": file.filename,
        "estado": estado,
        "url": url        
    })

@app.put("/aviso/editar/{id_aviso}", status_code=status.HTTP_200_OK, summary="Endpoint para editar un aviso existente en el carrusel de imágenes", tags=['Carrusel'])
async def editar_aviso(
    id_aviso: int,
    estado: int = Form(...),
    url: str = Form(...),
    file: UploadFile = File(None)  # Archivo opcional para la edición
):
    if estado not in [0, 1]:
        raise HTTPException(status_code=400, detail="El valor de 'estado' debe ser '0' o '1'")
    estado = str(estado) # Convertimos a str el estado y permisos para que no tome como posicion el valor
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    if file:
        # Guardar temporalmente el archivo
        file_location = f"static/temp/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Abrir la imagen y comprobar el tamaño
        try:
            with Image.open(file_location) as img:
                if img.size < (200, 200):
                    raise HTTPException(status_code=400, detail="La imagen tiene que ser mayor a 200x200")
                elif img.size > (1500, 1500):
                    raise HTTPException(status_code=400, detail="La imagen tiene que ser menor a 1500x1500")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Mover el archivo al directorio final si pasa las validaciones
        final_location = f"static/images/carrusel/{file.filename}"
        shutil.move(file_location, final_location)

        # Actualizar los datos en la base de datos
        query = 'UPDATE carrusel SET imagen=%s, ruta=%s, estado=%s, url=%s WHERE id_imagen=%s'
        usuario_data = (file.filename, "static/images/carrusel/", estado, url, id_aviso)
    else:
        # Actualizar los datos en la base de datos sin cambiar la imagen
        query = 'UPDATE carrusel SET estado=%s, url=%s WHERE id_imagen=%s'
        usuario_data = (estado, url, id_aviso)

    cursor.execute(query, usuario_data)
    connection.commit()

    return JSONResponse(content={
        "aviso_id": id_aviso,
        "estado": estado,
        "url": url,
        "filename": file.filename if file else "No se cambió la imagen"
    })

@app.delete("/aviso/borrar/{id_aviso}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un aviso existente en el carrusel de imágenes", tags=['Carrusel'])
async def borrar_aviso(id_aviso: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT imagen FROM carrusel WHERE id_imagen=%s", (id_aviso,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Aviso no encontrado")

    # Obtener el nombre del archivo
    file_name = aviso[0]
    file_path = f"static/images/carrusel/{file_name}"

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM carrusel WHERE id_imagen=%s", (id_aviso,))
    connection.commit()

    # Eliminar el archivo de imagen si existe
    if os.path.exists(file_path):
        os.remove(file_path)

    return JSONResponse(content={"message": "Aviso borrado correctamente", "aviso_id": id_aviso})

@app.get("/ubicacion",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las ubicaciones existentes", tags=['Mapa-Ubicaciones'])
def listar_ubicaciones():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM ubicaciones")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_ubicacion': row[0],
                    'latitud': row[1],
                    'longitud':row[2],
                    'lugar':row[3]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay ubicaciones en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/ubicacion/{id_ubicacion}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar una ubicacion en la bd", tags=['Mapa-Ubicaciones'])
def detalle_ubicacion(id_ubicacion:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM ubicaciones WHERE id_ubicacion = %s;"
        cursor.execute(query, (id_ubicacion,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_ubicacion': row[0],
                    'latitud': row[1],
                    'longitud':row[2],
                    'lugar':row[3]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe esa ubicacion en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/ubicacion/crear",status_code=status.HTTP_200_OK, summary="Endpoint para crear una ubicacion en el mapa", tags=['Mapa-Ubicaciones'])
def crear_ubicaciones(ubicaciones:Ubicaciones):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nuevo usuario en la base de datos
        query = "INSERT INTO ubicaciones (latitud, longitud, lugar) VALUES (%s, %s, %s)"
        usuario_data = (ubicaciones.latitud, ubicaciones.longitud, ubicaciones.lugar)
        cursor.execute(query, usuario_data)
        connection.commit()
        return {
            "latitud":ubicaciones.latitud,
            "longitud":ubicaciones.longitud,
            "lugar":ubicaciones.lugar
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar ubicacion en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear ubicacion")
    finally:
        cursor.close()
        connection.close()

@app.put("/ubicacion/editar/{id_ubicacion}",status_code=status.HTTP_200_OK, summary="Endpoint para editar una ubicacion en el mapa", tags=['Mapa-Ubicaciones'])
def editar_ubicacion(ubicaciones:Ubicaciones, id_ubicacion:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nuevo usuario en la base de datos
        query = 'UPDATE ubicaciones SET latitud=%s, longitud=%s, lugar =%s WHERE id_ubicacion=%s'
        usuario_data = (ubicaciones.latitud, ubicaciones.longitud, ubicaciones.lugar, id_ubicacion)
        cursor.execute(query, usuario_data)
        connection.commit()
        return {
            "latitud":ubicaciones.latitud,
            "longitud":ubicaciones.longitud,
            "lugar":ubicaciones.lugar
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar ubicacion en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar ubicacion")
    finally:
        cursor.close()
        connection.close()

@app.delete("/ubicacion/borrar/{id_ubicacion}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar una ubicacion existente en el mapa", tags=['Mapa-Ubicaciones'])
def borrar_ubicacion(id_ubicacion: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT * FROM ubicaciones WHERE id_ubicacion=%s", (id_ubicacion,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Ubicacion no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM ubicaciones WHERE id_ubicacion=%s", (id_ubicacion,))
    connection.commit()

    return JSONResponse(content={"message": "Ubicacion borrada correctamente", "id_ubicacion": id_ubicacion})

@app.get("/contacto",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los contactos existentes", tags=['Contactos'])
def listar_contactos():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM contactos")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_contacto': row[0],
                    'nombre_institucion': row[1],
                    'tipo_contacto':row[2],
                    'contacto':row[3],
                    'horario':row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay contactos en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/contacto/{id_contacto}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar un contacto en la bd", tags=['Contactos'])
def detalle_contacto(id_contacto:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM contactos WHERE id_contactos = %s"
        cursor.execute(query, (id_contacto,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_contacto': row[0],
                    'nombre_institucion': row[1],
                    'tipo_contacto':row[2],
                    'contacto':row[3],
                    'horario':row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe ese contacto en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/contacto/crear",status_code=status.HTTP_200_OK, summary="Endpoint para crear un contacto", tags=['Contactos'])
def crear_contacto(contacto:Contacto):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        if contacto.tipo_contacto not in ['telefono','email']:
            raise HTTPException(status_code=500, detail="El tipo de contacto solo puede ser 'telefono' o  'email'")


        # Insertar nuevo usuario en la base de datos
        query = "INSERT INTO contactos (nombre_institucion, tipo_contacto, contacto, horario) VALUES (%s, %s, %s, %s)"
        usuario_data = (contacto.nombre_institucion, contacto.tipo_contacto, contacto.contacto, contacto.horario)
        cursor.execute(query, usuario_data)
        connection.commit()
        return {
            'nombre_institucion': contacto.nombre_institucion,
            'tipo_contacto':contacto.tipo_contacto,
            'contacto': contacto.contacto,
            'horario': contacto.horario
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar contacto en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear contacto")
    finally:
        cursor.close()
        connection.close()

@app.put("/contacto/editar/{id_contacto}",status_code=status.HTTP_200_OK, summary="Endpoint para editar un contacto", tags=['Contactos'])
def editar_contacto(contacto:Contacto, id_contacto:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nuevo usuario en la base de datos
        query = 'UPDATE contactos SET nombre_institucion= %s, tipo_contacto= %s, contacto= %s, horario= %s WHERE id_contactos=%s'
        usuario_data = (contacto.nombre_institucion, contacto.tipo_contacto, contacto.contacto, contacto.horario, id_contacto)
        cursor.execute(query, usuario_data)
        connection.commit()
        return {
            'id_contacto': id_contacto,
            'nombre_institucion': contacto.nombre_institucion,
            'tipo_contacto':contacto.tipo_contacto,
            'contacto': contacto.contacto,
            'horario': contacto.horario
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar contacto en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar contacto")
    finally:
        cursor.close()
        connection.close()

@app.delete("/contacto/borrar/{id_contacto}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un contacto", tags=['Contactos'])
def borrar_contacto(id_contacto: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT * FROM contactos WHERE id_contactos=%s", (id_contacto,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM contactos WHERE id_contactos =%s", (id_contacto,))
    connection.commit()

    return JSONResponse(content={"message": "Contacto borrado correctamente", "id_contacto": id_contacto})

@app.get("/noticia",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las noticias existentes", tags=['Noticias'])
def listar_noticias():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM noticias")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_titulo': row[0],
                    'titulo': row[1],
                    'contenido':row[2],
                    'imagen':row[3],
                    'ruta':row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay noticias en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/noticia/{id_noticia}",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las noticias existentes", tags=['Noticias'])
def detalle_noticia(id_noticia:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM noticias WHERE id_noticia = %s"
        cursor.execute(query, (id_noticia,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_titulo': row[0],
                    'titulo': row[1],
                    'contenido':row[2],
                    'imagen':row[3],
                    'ruta':row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay noticias con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/noticia/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear una noticia y que se vea reflejado en la seccion de preguntas", tags=['Noticias'])
async def crear_noticia(
    titulo: str = Form(...),
    contenido: str = Form(...),
    file: UploadFile = File(...)
):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Guardar temporalmente el archivo
    file_location = f"static/temp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Abrir la imagen y comprobar el tamaño
    try:
        with Image.open(file_location) as img:
            if img.size < (200, 200):
                raise HTTPException(status_code=400, detail="La imagen tiene que ser mayor a 200x200")
            elif img.size > (1500, 1500):
                raise HTTPException(status_code=400, detail="La imagen tiene que ser menor a 1500x1500")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Mover el archivo al directorio final si pasa las validaciones
    final_location = f"static/images/noticias/{file.filename}"
    shutil.move(file_location, final_location)

    # Insertar datos en la base de datos
    query = 'INSERT INTO noticias (titulo, contenido, imagen, ruta) VALUES (%s,%s,%s,%s)'
    usuario_data = (titulo, contenido,file.filename, 'static/images/noticias/')
    cursor.execute(query, usuario_data)
    connection.commit()

    return JSONResponse(content={
        'titulo': titulo,
        'contenido':contenido,
        'imagen': file.filename,
        'ruta':'static/images/noticias/'
    })

@app.put("/noticia/editar/{id_noticia}", status_code=status.HTTP_200_OK, summary="Endpoint para editar una noticia existente", tags=['Noticias'])
async def editar_noticia(
    id_noticia: int,
    titulo: str = Form(...),
    contenido: str = Form(...),
    file: UploadFile = File(None)  # Archivo opcional para la edición
):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    if file:
        # Guardar temporalmente el archivo
        file_location = f"static/temp/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Abrir la imagen y comprobar el tamaño
        try:
            with Image.open(file_location) as img:
                if img.size < (200, 200):
                    raise HTTPException(status_code=400, detail="La imagen tiene que ser mayor a 200x200")
                elif img.size > (1500, 1500):
                    raise HTTPException(status_code=400, detail="La imagen tiene que ser menor a 1500x1500")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Mover el archivo al directorio final si pasa las validaciones
        final_location = f"static/images/noticias/{file.filename}"
        shutil.move(file_location, final_location)

        # Actualizar los datos en la base de datos
        query = 'UPDATE noticias SET titulo=%s, contenido=%s, imagen=%s WHERE id_noticia=%s'
        usuario_data = (titulo,contenido,file.filename,id_noticia)
    else:
        # Actualizar los datos en la base de datos sin cambiar la imagen
        query = 'UPDATE noticias SET titulo=%s, contenido=%s WHERE id_noticia=%s'
        usuario_data = (titulo,id_noticia)

    cursor.execute(query, usuario_data)
    connection.commit()

    return JSONResponse(content={
        "id_noticia": id_noticia,
        "titulo": titulo,
        "imagen": file.filename if file else "No se cambió la imagen"        
    })

@app.delete("/noticia/borrar/{id_noticia}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar una noticia existente", tags=['Noticias'])
async def borrar_noticia(id_noticia: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT * FROM noticias WHERE id_noticia=%s", (id_noticia,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    
    cursor.execute("SELECT imagen FROM noticias WHERE id_noticia=%s", (id_noticia,))
    aviso = cursor.fetchone()
    

    # Obtener el nombre del archivo
    file_name = aviso[0]
    file_path = f"static/images/noticias/{file_name}"

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM noticias WHERE id_noticia=%s", (id_noticia,))
    connection.commit()

    # Eliminar el archivo de imagen si existe
    if os.path.exists(file_path):
        os.remove(file_path)

    return JSONResponse(content={"message": "Noticia borrada correctamente", "id_noticia": id_noticia})

@app.get("/evento",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los eventos existentes", tags=['Eventos'])
def listar_eventos():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM eventos")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    "id_evento":row[0],
                    "titulo": row[1],
                    "descripcion":row[2],
                    "fecha":row[3],
                    "hora":row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay eventos en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/evento/{id_evento}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar un evento en la bd", tags=['Eventos'])
def detalle_evento(id_evento:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM eventos WHERE id_evento = %s"
        cursor.execute(query, (id_evento,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    "id_evento":row[0],
                    "titulo": row[1],
                    "descripcion":row[2],
                    "fecha":row[3],
                    "hora":row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe ese evento en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/evento/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un evento", tags=['Eventos'])
def crear_evento(evento: Evento):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nuevo evento en la base de datos
        query = "INSERT INTO eventos (titulo, descripcion, fecha, hora) VALUES (%s, %s, %s, %s)"
        evento_data = (evento.titulo, evento.descripcion, evento.fecha, evento.hora)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'titulo': evento.titulo,
            'descripcion': evento.descripcion,
            'fecha': evento.fecha,
            'hora': evento.hora
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar evento en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear evento")
    finally:
        cursor.close()
        connection.close()

@app.put("/evento/editar/{id_evento}",status_code=status.HTTP_200_OK, summary="Endpoint para editar un evento", tags=['Eventos'])
def editar_evento(evento: Evento, id_evento:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nuevo usuario en la base de datos
        query = "UPDATE eventos  SET titulo= %s, descripcion= %s, fecha= %s, hora= %s WHERE id_evento = %s"
        evento_data = (evento.titulo, evento.descripcion, evento.fecha, evento.hora, id_evento)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_evento':id_evento,
            'titulo': evento.titulo,
            'descripcion': evento.descripcion,
            'fecha': evento.fecha,
            'hora': evento.hora
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar evento en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar evento")
    finally:
        cursor.close()
        connection.close()

@app.delete("/evento/borrar/{id_evento}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un contacto", tags=['Eventos'])
def borrar_evento(id_evento: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT * FROM eventos WHERE id_evento=%s", (id_evento,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Ubicacion no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM eventos WHERE id_evento =%s", (id_evento,))
    connection.commit()

    return JSONResponse(content={"message": "Aviso borrado correctamente", "aviso_id": id_evento})

@app.get("/bot",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los contactos existentes", tags=['ChatBot'])
def listar_bot():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM bot")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id': row[0],
                    'nombre': row[1],
                    'correo':row[2],
                    'problema':row[3],
                    'area':row[4]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay problemas con el bot en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/bot/{id_bot}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar un asunto con el Bot en la bd", tags=['ChatBot'])
def detalle_bot(id_bot:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM bot WHERE id = %s"
        cursor.execute(query, (id_bot,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id': row[0],
                    'nombre': row[1],
                    'correo':row[2],
                    'problema':row[3],
                    'area':row[4]
                }
                respuesta.append(dato)
            

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe ese problema con el bot en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/bot/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un asunto", tags=['ChatBot'])
def crear_bot(bot: Bot):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nuevo evento en la base de datos
        query = "INSERT INTO bot (nombre, correo, problema,area) VALUES (%s, %s, %s, %s)"
        evento_data = (bot.nombre, bot.correo, bot.problema, bot.area)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'nombre': bot.nombre,
            'correo': bot.correo,
            'problema': bot.problema,
            'area': bot.area
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar un problema con el bot en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear un problema con el bot")
    finally:
        cursor.close()
        connection.close()

@app.put("/bot/editar/{id_bot}",status_code=status.HTTP_200_OK, summary="Endpoint para editar un asunto con el bot en la base de datos", tags=['ChatBot'])
def editar_bot(bot: Bot, id_bot:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nuevo usuario en la base de datos
        query = "UPDATE bot SET nombre = %s, correo= %s, problema= %s, area = %s WHERE id = %s"
        evento_data = (bot.nombre,bot.correo,bot.problema,bot.area, id_bot)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'nombre': bot.nombre,
            'correo': bot.correo,
            'problema': bot.problema,
            'area':bot.area
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar problema con el bot en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar problema con el bot")
    finally:
        cursor.close()
        connection.close()

@app.delete("/bot/editar/{id_bot}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un contacto", tags=['ChatBot'])
def borrar_bot(id_bot: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT * FROM bot WHERE id=%s", (id_bot,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Ubicacion no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM bot WHERE id =%s", (id_bot,))
    connection.commit()

    return JSONResponse(content={"message": "Aviso borrado correctamente", "aviso_id": id_bot})

@app.get("/encuesta",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las encuestas existentes", tags=['Encuestas'])
def listar_encuestas():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM encuestas")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_encuesta': row[0],
                    'titulo': row[1],
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay encuestas en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/encuesta/{id_encuesta}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar una encuesta en la bd", tags=['Encuestas'])
def detalle_encuesta(id_encuesta:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM encuesta WHERE id_encuesta = %s"
        cursor.execute(query, (id_encuesta,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_encuesta': row[0],
                    'titulo': row[1],
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe esa encuesta la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/encuesta/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear una encuesta", tags=['Encuestas'])
def crear_encuesta(encuestas: Encuestas):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nueva encuesta en la base de datos
        query = "INSERT INTO encuestas (titulo) VALUES (%s)"
        encuesta_data = (encuestas.titulo,)
        cursor.execute(query, encuesta_data)
        connection.commit()
        
        # Obtener el ID del registro insertado
        encuesta_id = cursor.lastrowid
        
        return {
            'id': encuesta_id,
            'titulo': encuestas.titulo,
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar encuesta en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear una encuesta")
    finally:
        cursor.close()
        connection.close()

@app.put("/encuesta/editar/{id_encuesta}",status_code=status.HTTP_200_OK, summary="Endpoint para editar una encuesta", tags=['Encuestas'])
def editar_encuesta(encuestas: Encuestas, id_encuesta:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar nuevo usuario en la base de datos
        query = "UPDATE encuestas SET titulo= %s WHERE id_encuesta = %s"
        evento_data = (encuestas.titulo, id_encuesta)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_encuesta':id_encuesta,
            'titulo':encuestas.titulo
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar evento en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar evento")
    finally:
        cursor.close()
        connection.close()

@app.delete("/encuesta/borrar/{id_encuesta}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar una encuesta", tags=['Encuestas'])
def borrar_encuesta(id_encuesta: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT * FROM encuestas WHERE id_encuesta =%s", (id_encuesta,))
    encuesta = cursor.fetchone()
    
    if not encuesta:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM opcion WHERE id_encuesta =%s", (id_encuesta,))
    cursor.execute("DELETE FROM preguntas WHERE id_encuesta =%s", (id_encuesta,))
    cursor.execute("DELETE FROM encuestas WHERE id_encuesta =%s", (id_encuesta,))
    connection.commit()

    return JSONResponse(content={"message": "Aviso borrado correctamente", "aviso_id": id_encuesta})

@app.get("/pregunta",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las encuestas existentes", tags=['Preguntas'])
def listar_preguntas():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM preguntas")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_pregunta': row[0],
                    'id_encuesta': row[1],
                    'pregunta': row[2],
                    'pregunta_abierta':row[3],
                    'pregunta_cerrada_multiple':row[4]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay preguntas en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/pregunta/{id_pregunta}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar una pregunta en la bd", tags=['Preguntas'])
def detalle_pregunta(id_pregunta:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM pregunta WHERE id_pregunta = %s"
        cursor.execute(query, (id_pregunta,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_pregunta': row[0],
                    'id_encuesta': row[1],
                    'pregunta': row[2],
                    'pregunta_abierta':row[3],
                    'pregunta_cerrada_multiple':row[4]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe esa encuesta la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/pregunta/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear una pregunta", tags=['Preguntas'])
def crear_pregunta(pregunta: Preguntas):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Verificar si el id_encuesta existe en la tabla encuestas
        query_check_encuesta = "SELECT 1 FROM encuestas WHERE id_encuesta = %s"
        cursor.execute(query_check_encuesta, (pregunta.id_encuesta,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La encuesta no existe")
        
        # Validar los valores de pregunta_abierta y pregunta_cerrada_multiple
        if pregunta.pregunta_abierta not in [0, 1]:
            raise HTTPException(status_code=400, detail="El valor de 'pregunta_abierta' debe ser '0' o '1'")
        if pregunta.pregunta_cerrada_multiple not in [0, 1]:
            raise HTTPException(status_code=400, detail="El valor de 'pregunta_cerrada_multiple' debe ser '0' o '1'")
        
        # Insertar nueva pregunta en la base de datos
        query = "INSERT INTO preguntas (id_encuesta, pregunta, pregunta_abierta, pregunta_cerrada_multiple) VALUES (%s,%s,%s,%s)"
        pregunta_data = (pregunta.id_encuesta, pregunta.pregunta, pregunta.pregunta_abierta, pregunta.pregunta_cerrada_multiple)
        cursor.execute(query, pregunta_data)
        connection.commit()
        
        # Obtener el ID del registro insertado
        pregunta_id = cursor.lastrowid

        return {
            'id_pregunta': pregunta_id,
            'id_encuesta': pregunta.id_encuesta,
            'pregunta': pregunta.pregunta,
            'pregunta_abierta': pregunta.pregunta_abierta,
            'pregunta_cerrada_multiple': pregunta.pregunta_cerrada_multiple
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar pregunta en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear una pregunta")
    finally:
        cursor.close()
        connection.close()
        
@app.put("/pregunta/editar/{id_pregunta}", status_code=status.HTTP_200_OK, summary="Endpoint para editar una pregunta", tags=['Preguntas'])
def editar_pregunta(pregunta: EditarPregunta, id_pregunta: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Verificar si el id_encuesta existe en la tabla encuestas
        query_check_encuesta = "SELECT 1 FROM encuestas WHERE id_encuesta = %s"
        cursor.execute(query_check_encuesta, (pregunta.id_encuesta,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La encuesta no existe")
        
        # Actualizar pregunta en la base de datos
        query = "UPDATE preguntas SET pregunta = %s WHERE id_pregunta = %s"
        evento_data = (pregunta.pregunta)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'detail': 'pregunta actualizada correctamente',
            'pregunta': pregunta.pregunta
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar la pregunta en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar pregunta")
    finally:
        cursor.close()
        connection.close()

@app.delete("/pregunta/borrar/{id_pregunta}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar una encuesta", tags=['Preguntas'])
def borrar_pregunta(id_pregunta: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT * FROM preguntas WHERE id_pregunta =%s", (id_pregunta,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Ubicacion no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM opcion WHERE id_encuesta =%s", (id_pregunta,))
    cursor.execute("DELETE FROM preguntas WHERE id_pregunta =%s", (id_pregunta,))
    connection.commit()

    return JSONResponse(content={"message": "Aviso borrado correctamente", "id_pregunta": id_pregunta})

@app.get("/opcion",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las opciones existentes", tags=['Opciones'])
def listar_opciones():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM opcion")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_opcion':row[0],
                    'id_pregunta': row[1],
                    'id_encuesta': row[2],
                    'opcion': row[3]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay opciones en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/opcion/{id_opcion}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar una opcion en la bd", tags=['Opciones'])
def detalle_opcion(id_opcion:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM opcion WHERE id_opcion = %s"
        cursor.execute(query, (id_opcion,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_opcion':row[0],
                    'id_pregunta': row[1],
                    'id_encuesta': row[2],
                    'opcion': row[3]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe esa opcion en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/opcion/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear una opcion", tags=['Opciones'])
def crear_opcion(opcion:Opciones):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Verificar si el id_encuesta existe en la tabla encuestas
        query_check_encuesta = "SELECT 1 FROM encuestas WHERE id_encuesta = %s"
        cursor.execute(query_check_encuesta, (opcion.id_encuesta,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La encuesta no existe")
        
        # Verificar si el id_pregunta existe en la tabla encuestas
        query_check_pregunta_1 = "SELECT 1 FROM preguntas WHERE id_pregunta = %s"
        cursor.execute(query_check_pregunta_1, (opcion.id_pregunta,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La pregunta no existe")
        
        # Verificar si el id_pregunta existe en la tabla encuestas
        query_check_pregunta_1 = "SELECT 1 FROM preguntas WHERE id_pregunta = %s AND pregunta_abierta = %s"
        cursor.execute(query_check_pregunta_1, (opcion.id_pregunta,'1'))
        if cursor.fetchone() is not None:
            raise HTTPException(status_code=404, detail="La pregunta es abierta, porque deberia tener opciones????")

        # Insertar nuevo evento en la base de datos
        query = "INSERT INTO opcion (id_pregunta, id_encuesta, opcion) VALUES (%s,%s,%s)"
        evento_data = (opcion.id_pregunta, opcion.id_encuesta, opcion.opcion)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_pregunta': opcion.id_pregunta,
            'id_encuesta': opcion.id_encuesta,
            'opcion': opcion.opcion
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar pregunta en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear una opcion")
    finally:
        cursor.close()
        connection.close()

@app.put("/opcion/editar/{id_opcion}", status_code=status.HTTP_200_OK, summary="Endpoint para editar una opcion", tags=['Opciones'])
def editar_opcion(opcion:EditarOpcion, id_opcion: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar pregunta en la base de datos
        query = "UPDATE opcion SET opcion = %s WHERE id_opcion = %s"
        evento_data = (opcion, id_opcion)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'opcion': opcion.opcion
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar la opcion en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar opcion")
    finally:
        cursor.close()
        connection.close()

@app.delete("/opcion/borrar/{id_opcion}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar una opcion", tags=['Opciones'])
def borrar_opcion(id_opcion: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si el aviso existe y obtener la información del archivo
    cursor.execute("SELECT * FROM opcion WHERE id_opcion =%s", (id_opcion,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Ubicacion no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM opcion WHERE id_opcion =%s", (id_opcion,))
    connection.commit()

    return JSONResponse(content={"message": "Aviso borrado correctamente", "id_pregunta": id_opcion})

@app.get("/respuesta_abierta",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las respuestas abiertas dadas existentes", tags=['Respuestas_abiertas'])
def listar_respuestas_abiertas():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM respuesta_abierta")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_respuesta_abierta':row[0],
                    'id_pregunta': row[1],
                    'id_encuesta': row[2],
                    'respuesta': row[3]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay respuestas abiertas en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/respuesta_abierta/{id_respuesta_abierta}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar una respuesta abierta en la bd", tags=['Respuestas_abiertas'])
def detalle_respuesta_abierta(id_respuesta_abierta:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM respuesta_abierta WHERE id_respuesta_abierta = %s"
        cursor.execute(query, (id_respuesta_abierta,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_respuesta_abierta':row[0],
                    'id_pregunta': row[1],
                    'id_encuesta': row[2],
                    'respuesta': row[3]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe una respuesta abierta con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/respuesta_abierta/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear una respuesta abierta", tags=['Respuestas_abiertas'])
def crear_respuesta_abierta(respuesta:Respuesta_abierta):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Verificar si el id_encuesta existe en la tabla encuestas
        query_check_encuesta = "SELECT 1 FROM encuestas WHERE id_encuesta = %s"
        cursor.execute(query_check_encuesta, (respuesta.id_encuesta,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La encuesta no existe")
        
        # Verificar si el id_pregunta existe en la tabla encuestas
        query_check_pregunta_1 = "SELECT 1 FROM preguntas WHERE id_pregunta = %s"
        cursor.execute(query_check_pregunta_1, (respuesta.id_pregunta,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La pregunta no existe")
        
        # Verificar si el id_pregunta existe en la tabla encuestas
        query_check_pregunta_1 = "SELECT 1 FROM preguntas WHERE id_pregunta = %s AND pregunta_abierta = %s"
        cursor.execute(query_check_pregunta_1, (respuesta.id_pregunta,0))
        if cursor.fetchone() is not None:
            raise HTTPException(status_code=404, detail="La pregunta es cerrada, no deberias poner opciones ahi")

        # Insertar nuevo evento en la base de datos
        query = "INSERT INTO respuesta_abierta (id_pregunta, id_encuesta, respuesta) VALUES (%s,%s,%s)"
        evento_data = (respuesta.id_pregunta, respuesta.id_encuesta, respuesta.respuesta)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_pregunta': respuesta.id_pregunta,
            'id_encuesta': respuesta.id_encuesta,
            'respuesta': respuesta.respuesta
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar pregunta en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear una opcion")
    finally:
        cursor.close()
        connection.close()

@app.put("/respuesta_abierta/editar/{id_pregunta_abierta}", status_code=status.HTTP_200_OK, summary="Endpoint para editar una respuesta_abierta", tags=['Respuestas_abiertas'])
def editar_respuesta_abierta(respuesta:Editar_respuesta_abierta, id_pregunta_abierta: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar respuesta abierta en la base de datos
        query = "UPDATE respuesta_abierta SET respuesta = %s WHERE id_respuesta_abierta = %s"
        evento_data = (respuesta.respuesta, id_pregunta_abierta)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'nueva respuesta': respuesta.respuesta
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar la respuesta en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar la respuesta")
    finally:
        cursor.close()
        connection.close()

@app.delete("/respuesta_abierta/borrar/{id_respuesta_abierta}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar una respuesta abierta", tags=['Respuestas_abiertas'])
def borrar_respuesta_abierta(id_respuesta_abierta: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si la repuesta existe
    cursor.execute("SELECT * FROM respuesta_abierta WHERE id_respuesta_abierta =%s", (id_respuesta_abierta,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM respuesta_abierta WHERE id_respuesta_abierta =%s", (id_respuesta_abierta,))
    connection.commit()

    return JSONResponse(content={"message": "Respuesta borrada correctamente", "id_respuesta_abierta": id_respuesta_abierta})

@app.get("/respuesta_cerrada",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las respuestas cerradas existentes", tags=['Respuestas_cerradas'])
def listar_respuestas_cerradas():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM respuesta_cerrada")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_respuesta':row[0],
                    'id_opcion':row[1],
                    'id_pregunta': row[2],
                    'id_encuesta': row[3]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay respuestas cerradas en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/respuesta_cerrada/{id_respuesta_cerrada}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar una respuesta cerrada en la bd", tags=['Respuestas_cerradas'])
def detalle_respuesta_cerrada(id_respuesta_cerrada:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM respuesta_cerrada WHERE id_respuesta = %s"
        cursor.execute(query, (id_respuesta_cerrada,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_respuesta':row[0],
                    'id_opcion':row[1],
                    'id_pregunta': row[2],
                    'id_encuesta': row[3]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe una respuesta cerrada con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/respuesta_cerrada/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear una respuesta cerrada", tags=['Respuestas_cerradas'])
def crear_respuesta_cerrada(respuesta:Respuesta_cerrada):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Verificar si el id_encuesta existe en la tabla encuestas
        query_check_encuesta = "SELECT 1 FROM encuestas WHERE id_encuesta = %s"
        cursor.execute(query_check_encuesta, (respuesta.id_encuesta,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La encuesta no existe")
        
        # Verificar si el id_pregunta existe en la tabla preguntas
        query_check_pregunta_1 = "SELECT 1 FROM preguntas WHERE id_pregunta = %s"
        cursor.execute(query_check_pregunta_1, (respuesta.id_pregunta,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La pregunta no existe")
        
        # Verificar si la pregunta es abierta o cerrada
        query_check_pregunta_1 = "SELECT 1 FROM preguntas WHERE id_pregunta = %s AND pregunta_abierta = %s"
        cursor.execute(query_check_pregunta_1, (respuesta.id_pregunta,1))
        if cursor.fetchone() is not None:
            raise HTTPException(status_code=404, detail="La pregunta es abierta, como se supone que va a hacer eso??")
        
        # Verificar si el id_opcion existe en la tabla opcion
        query_check_pregunta_1 = "SELECT 1 FROM opcion WHERE id_opcion = %s"
        cursor.execute(query_check_pregunta_1, (respuesta.id_opcion,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="La opcion no existe")

        # Insertar una respesta cerrada en la base de datos
        query = "INSERT INTO respuesta_cerrada (id_opcion, id_pregunta, id_encuesta) VALUES (%s,%s,%s)"
        evento_data = (respuesta.id_opcion, respuesta.id_pregunta, respuesta.id_encuesta)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_opcion': respuesta.id_opcion,
            'id_pregunta': respuesta.id_pregunta,
            'id_encuesta': respuesta.id_encuesta
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar pregunta en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear una opcion")
    finally:
        cursor.close()
        connection.close()

@app.put("/respuesta_cerrada/editar/{id_pregunta_cerrada}", status_code=status.HTTP_200_OK, summary="Endpoint para editar una respuesta cerrada", tags=['Respuestas_cerradas'])
def editar_respuesta_cerrada(respuesta:Editar_respuesta_cerrada, id_pregunta_abierta: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar respuesta abierta en la base de datos
        query = "UPDATE respuesta_abierta SET respuesta = %s WHERE id_respuesta_abierta = %s"
        evento_data = (respuesta.id_opcion, id_pregunta_abierta)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'nueva opcion seleccionada': respuesta.id_opcion
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar la respuesta en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar la respuesta")
    finally:
        cursor.close()
        connection.close()

@app.delete("/respuesta_cerrada/borrar/{id_respuesta_cerrada}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar una respuesta cerrada", tags=['Respuestas_cerradas'])
def borrar_respuesta_cerrada(id_respuesta_cerrada: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si la repuesta existe
    cursor.execute("SELECT * FROM respuesta_cerrada WHERE id_respuesta =%s", (id_respuesta_cerrada,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM respuesta_cerrada WHERE id_respuesta =%s", (id_respuesta_cerrada,))
    connection.commit()

    return JSONResponse(content={"message": "Respuesta borrada correctamente", "id_respuesta_cerrada": id_respuesta_cerrada})

@app.get("/articulo",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los articulos existentes", tags=['Articulos'])
def listar_articulos():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM articulos")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_articulo':row[0],
                    'num_articulo':row[1]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay articulos en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/articulo/{id_articulo}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar articulos en la bd", tags=['Articulos'])
def detalle_articulo(id_articulo:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM articulos WHERE id_articulo = %s"
        cursor.execute(query, (id_articulo,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_articulo':row[0],
                    'num_articulo':row[1]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe un articulo con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/articulo/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un articulo", tags=['Articulos'])
def crear_articulo(articulo:Articulo):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar una respesta cerrada en la base de datos
        query = "INSERT INTO articulos (num_articulo) VALUES (%s)"
        evento_data = (articulo.num_articulo, )
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'num_articulo': articulo.num_articulo
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar articulo en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear un articulo")
    finally:
        cursor.close()
        connection.close()

@app.put("/articulo/editar/{id_articulo}", status_code=status.HTTP_200_OK, summary="Endpoint para editar un articulo", tags=['Articulos'])
def editar_articulo(articulo:Articulo, id_articulo: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar respuesta abierta en la base de datos
        query = "UPDATE articulos SET num_articulo = %s WHERE id_articulo = %s"
        evento_data = (articulo.num_articulo, id_articulo)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'Nueva articulo editado': articulo.num_articulo
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar el articulo en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar el articulo")
    finally:
        cursor.close()
        connection.close()

@app.delete("/articulo/borrar/{id_articulo}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un articulo", tags=['Articulos'])
def borrar_articulo(id_articulo: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si la repuesta existe
    cursor.execute("SELECT * FROM articulos WHERE id_articulo =%s", (id_articulo,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Articulo no encontrado")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM articulos WHERE id_articulo =%s", (id_articulo,))
    connection.commit()

    return JSONResponse(content={"message": "Articulo borrado correctamente", "id_articulo": id_articulo})

@app.get("/fraccion",status_code=status.HTTP_200_OK, summary="Endpoint para listar todas las fracciones existentes", tags=['Fracciones'])
def listar_fraccion():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM fracciones")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_fraccion':row[0],
                    'fraccion':row[1],
                    'descripcion': row[2],
                    'area': row[3],
                    'num_articulo': row[4]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay fracciones en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/fraccion/{id_fraccion}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar fracciones en la bd", tags=['Fracciones'])
def detalle_fraccion(id_fraccion:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM fracciones WHERE id_fraccion = %s"
        cursor.execute(query, (id_fraccion,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_fraccion':row[0],
                    'fraccion':row[1],
                    'descripcion': row[2],
                    'area': row[3],
                    'num_articulo': row[4]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe una fraccion con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/fracciones/busqueda", status_code=status.HTTP_200_OK, summary="Buscar fracciones por área y/o número de artículo", tags=['Fracciones'])
def buscar_fracciones(area: str = Query(None, description="Nombre del área a buscar"), num_articulo: str = Query(None, description="Número del artículo a buscar")):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Contruir la consulta SQL dinámicamente según los parámetros proporcionados
    base_query = "SELECT * FROM fracciones WHERE"
    conditions = []
    parameters = []

    if area:
        conditions.append(" area = %s")
        parameters.append(area)

    if num_articulo:
        conditions.append(" num_articulo = %s")
        parameters.append(num_articulo)

    # Verifica que al menos un parámetro haya sido proporcionado
    if not conditions:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un parámetro de búsqueda")

    query = base_query + " AND".join(conditions)
    try:
        cursor.execute(query, parameters)
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_fraccion': row[0],
                    'fraccion': row[1],
                    'descripcion': row[2],
                    'area': row[3],
                    'num_articulo': row[4]
                }
                respuesta.append(dato)
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No se encontraron fracciones con los criterios especificados")
    finally:
        cursor.close()
        connection.close()

@app.post("/fraccion/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear una fraccion", tags=['Fracciones'])
def crear_fraccion(fraccion:Fraccion):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar una respesta cerrada en la base de datos
        query = "INSERT INTO fracciones (fraccion, descripcion, area, num_articulo) VALUES (%s, %s, %s, %s)"
        evento_data = (fraccion.fraccion, fraccion.descripcion, fraccion.area, fraccion.num_articulo)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'fraccion':fraccion.fraccion,
            'descripcion': fraccion.descripcion,
            'area': fraccion.area,
            'id articulo': fraccion.num_articulo
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar fraccion en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear una fraccion")
    finally:
        cursor.close()
        connection.close()

@app.put("/fraccion/editar/{id_fraccion}", status_code=status.HTTP_200_OK, summary="Endpoint para editar una fraccion", tags=['Fracciones'])
def editar_fraccion(fraccion:Fraccion, id_fraccion: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar respuesta abierta en la base de datos
        query = "UPDATE fracciones SET fraccion = %s, descripcion = %s, area = %s, num_articulo = %s WHERE id_fraccion = %s"
        evento_data = (fraccion.fraccion, fraccion.descripcion, fraccion.area, fraccion.num_articulo, id_fraccion)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_fraccion': id_fraccion,
            'fraccion':fraccion.fraccion,
            'descripcion': fraccion.descripcion,
            'area': fraccion.area,
            'id articulo': fraccion.num_articulo
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar la fraccion en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar la fraccion")
    finally:
        cursor.close()
        connection.close()

@app.delete("/fraccion/borrar/{id_fraccion}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar una fraccion", tags=['Fracciones'])
def borrar_fraccion(id_fraccion: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si la repuesta existe
    cursor.execute("SELECT * FROM fracciones WHERE id_fraccion =%s", (id_fraccion,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Fraccion no encontrada")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM fracciones WHERE id_fraccion =%s", (id_fraccion,))
    connection.commit()

    return JSONResponse(content={"message": "Fraccion borrada correctamente", "id_fraccion": id_fraccion})

@app.get("/año",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los años existentes", tags=['Años'])
def listar_años():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM años")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_año':row[0],
                    'año':row[1],
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay años en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/año/{id_año}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar años en la bd", tags=['Años'])
def detalle_año(id_año:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM años WHERE id_año = %s"
        cursor.execute(query, (id_año,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_año':row[0],
                    'año':row[1],
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe un año con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()


    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar respuesta abierta en la base de datos
        query = "UPDATE años SET año = %s, id_fraccion = %s WHERE id_año = %s"
        evento_data = (año.año, año.id_fraccion, id_año)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_año':id_año,
            'año': año.año,
            'id_fraccion': año.id_fraccion
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar el año en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar el año")
    finally:
        cursor.close()
        connection.close()

@app.delete("/año/borrar/{id_año}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un año", tags=['Años'])
def borrar_año(id_año: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si la repuesta existe
    cursor.execute("SELECT * FROM años WHERE id_año =%s", (id_año,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Año no encontrado")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM años WHERE id_año =%s", (id_año,))
    connection.commit()

    return JSONResponse(content={"message": "Año borrado correctamente", "id_año": id_año})

@app.get("/documento",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los documentos existentes", tags=['Documentos'])
def listar_documentos():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM documentos")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_documento':row[0],
                    'documento':row[1],
                    'ruta':row[2],
                    'trimestre': row[3],
                    'año':row[4],
                    'id_fraccion':row[5]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay documentos en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/documento/{id_documento}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar un documento en la bd", tags=['Documentos'])
def detalle_documento(id_documento:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM documentos WHERE id_documento = %s"
        cursor.execute(query, (id_documento,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_documento':row[0],
                    'documento':row[1],
                    'ruta':row[2],
                    'trimestre': row[3],
                    'año':row[4],
                    'id_fraccion':row[5]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe un documento con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/documento/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un documento", tags=['Documentos'])
async def crear_documento(
    id_fraccion: int = Form(...),
    año: str = Form(...),
    trimestre: str = Form(...),
    file: UploadFile = File(...)):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Obtener el fraccion y num_articulo desde la base de datos
        cursor.execute("""
            SELECT f.fraccion, a.num_articulo 
            FROM fracciones f
            JOIN articulos a ON f.num_articulo = a.num_articulo
            WHERE f.id_fraccion = %s
        """, (id_fraccion,))
        fraccion_articulo = cursor.fetchone()
        
        if not fraccion_articulo:
            raise HTTPException(status_code=404, detail="Fracción o artículo no encontrado")
        
        fraccion, articulo = fraccion_articulo

        # Crear la ruta del archivo con la estructura especificada
        directory = os.path.join(f"static/documents/transparencia/{str(articulo)}/{fraccion}/{str(año)}")
        os.makedirs(directory, exist_ok=True)
        file_location = os.path.join(f"{directory}/{file.filename}")

        # Guardar el archivo localmente
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Insertar documento en la base de datos
        query = "INSERT INTO documentos (documento, ruta, trimestre, año, id_fraccion) VALUES (%s, %s ,%s, %s, %s)"
        evento_data = (file.filename, directory, trimestre, año, id_fraccion)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_documento': cursor.lastrowid,
            'documento': file.filename,
            'ruta': directory,
            'trimestre': trimestre,
            'año': año,
            'id_fraccion': id_fraccion,
            'ruta': file_location
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar documento en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear documento")
    finally:
        cursor.close()
        connection.close()

@app.delete("/documento/borrar/{id_documento}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un documento", tags=['Documentos'])
def borrar_documento(id_documento: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Verificar si el documento existe y obtener sus detalles
        cursor.execute("SELECT documento, año, id_fraccion FROM documentos WHERE id_documento = %s", (id_documento,))
        documento_data = cursor.fetchone()

        if not documento_data:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        documento, año, id_fraccion = documento_data

        # Obtener fraccion y num_articulo desde la base de datos
        cursor.execute("""
            SELECT f.fraccion, a.num_articulo 
            FROM fracciones f
            JOIN articulos a ON f.num_articulo = a.num_articulo
            WHERE f.id_fraccion = %s
        """, (id_fraccion,))
        fraccion_articulo = cursor.fetchone()
        
        if not fraccion_articulo:
            raise HTTPException(status_code=404, detail="Fracción o artículo no encontrado")
        
        fraccion, articulo = fraccion_articulo

        # Construir la ruta completa del archivo
        file_location = os.path.join(f"static/documents/transparencia/{str(articulo)}/{fraccion}/{str(año)}/{documento}")

        # Eliminar el archivo localmente
        if os.path.exists(file_location):
            os.remove(file_location)
        else:
            raise HTTPException(status_code=404, detail="Archivo no encontrado en el sistema de archivos")

        # Eliminar el documento de la base de datos
        cursor.execute("DELETE FROM documentos WHERE id_documento = %s", (id_documento,))
        connection.commit()

        return JSONResponse(content={"message": "Documento borrado correctamente", "id_documento": id_documento})
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al borrar el documento en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al borrar documento")
    finally:
        cursor.close()
        connection.close()

@app.get("/tramite",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los tramites y servicios existentes", tags=['Tramites y Servicios'])
def listar_tramites_servicios():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM tramites_servicios")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_tramite':row[0],
                    'nombre':row[1]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay tramites ni servicios en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/tramite/{id_tramite}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar tramites y servicios en la bd", tags=['Tramites y Servicios'])
def detalle_tramite_servicio(id_tramite:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM tramites_servicios WHERE id_tramite = %s"
        cursor.execute(query, (id_tramite,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_tramite':row[0],
                    'nombre':row[1]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe ningun tramite o servicio con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/tramite/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un tramite o servicio", tags=['Tramites y Servicios'])
def crear_tramite_servicio(tramite:Tramite):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar una respesta cerrada en la base de datos
        query = "INSERT INTO tramites_servicios (nombre) VALUES (%s)"
        evento_data = (tramite.nombre)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'nombre': tramite.nombre
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar articulo en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear un tramite o servicio")
    finally:
        cursor.close()
        connection.close()

@app.put("/tramite/editar/{id_tramite}", status_code=status.HTTP_200_OK, summary="Endpoint para editar un tramite o servicio", tags=['Tramites y Servicios'])
def editar_tramite_servicio(tramite:Tramite, id_tramite: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar respuesta abierta en la base de datos
        query = "UPDATE tramites_servicios SET nombre = %s WHERE id_tramite = %s"
        evento_data = (tramite.nombre, id_tramite)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'nombre nuevo': tramite.nombre
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar el tramite o servicio en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar el tramite o servicio")
    finally:
        cursor.close()
        connection.close()

@app.delete("/tramite/borrar/{id_tramite}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un tramite o servicio", tags=['Tramites y Servicios'])
def borrar_tramite_servicio(id_tramite: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si la repuesta existe
    cursor.execute("SELECT * FROM tramites_servicios WHERE id_tramite =%s", (id_tramite,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Articulo no encontrado")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM tramites_servicios WHERE id_tramite =%s", (id_tramite,))
    connection.commit()

    return JSONResponse(content={"message": "Tramite o servicio borrado correctamente", "id_tramite": id_tramite})

@app.get("/requisito",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los requisitos", tags=['Requisitos'])
def listar_tramites_servicios():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM requisitos")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_requisito':row[0],
                    'requisito':row[1],
                    'id_tramite':row[0]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay requisitos en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/requisito/{id_requisito}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar requisitos en la bd", tags=['Requisitos'])
def detalle_requisito(id_requisito:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM requisitos WHERE id_requisito = %s"
        cursor.execute(query, (id_requisito,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_requisito':row[0],
                    'requisito':row[1],
                    'id_tramite':row[0]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe ningun requisito con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/requisito/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un requisito", tags=['Requisitos'])
def crear_requisito(requisito:Requisito):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar una respesta cerrada en la base de datos
        query = "INSERT INTO tramites_servicios (requisito, id_tramite) VALUES (%s, %s)"
        evento_data = (requisito.requisito, requisito.id_tramite)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'requisito': requisito.requisito,
            'id_tramite': requisito.id_tramite
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar requisito en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear un requisito")
    finally:
        cursor.close()
        connection.close()

@app.put("/requisito/editar/{id_requisito}", status_code=status.HTTP_200_OK, summary="Endpoint para editar un requisito", tags=['Requisitos'])
def editar_requisito(requisito:Editar_requisito, id_requisito: int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar respuesta abierta en la base de datos
        query = "UPDATE requisitos SET requisito = %s WHERE id_requisito = %s"
        evento_data = (requisito.requisito, id_requisito)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_requisito':id_requisito,
            'nombre nuevo': requisito.requisito
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar el requisito en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar el requisito")
    finally:
        cursor.close()
        connection.close()

@app.delete("/requisito/borrar/{id_requisito}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un requisito", tags=['Requisitos'])
def borrar_requisito(id_requisito: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si la repuesta existe
    cursor.execute("SELECT * FROM requisitos WHERE id_requisito =%s", (id_requisito,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Requisito no encontrado")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM requisitos WHERE id_requisito =%s", (id_requisito,))
    connection.commit()

    return JSONResponse(content={"message": "Requisito borrado correctamente", "id_requisito": id_requisito})

@app.get("/color",status_code=status.HTTP_200_OK, summary="Endpoint para listar todos los colores existentes", tags=['Colores'])
def listar_colores():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM colores")
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_color':row[0],
                    'nombre_color':row[1],
                    'valor_hex': row[2]
                }
                respuesta.append(dato)
            
            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No hay colores en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.get("/color/{id_color}",status_code=status.HTTP_200_OK, summary="Endpoint para buscar colores en la bd", tags=['Colores'])
def detalle_color(id_color:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM colores WHERE id_color = %s"
        cursor.execute(query, (id_color,))
        datos = cursor.fetchall()
        if datos:
            respuesta = []
            for row in datos:
                dato = {
                    'id_color':row[0],
                    'nombre_color':row[1],
                    'valor_hex': row[2]
                }
                respuesta.append(dato)

            return respuesta
        else:
            raise HTTPException(status_code=404, detail="No existe un color con ese id en la Base de datos")
    finally:
        cursor.close()
        connection.close()

@app.post("/color/crear", status_code=status.HTTP_200_OK, summary="Endpoint para crear un color", tags=['Colores'])
def crear_color(color:Color):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Insertar una respesta cerrada en la base de datos
        query = "INSERT INTO colores (nombre_color, valor_hex) VALUES (%s, %s)"
        evento_data = (color.nombre_color, color.valor_hex)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'nombre_color': color.nombre_color,
            'valor_hex': color.valor_hex
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al insertar color en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al crear un color")
    finally:
        cursor.close()
        connection.close()

@app.put("/color/editar/{id_color}", status_code=status.HTTP_200_OK, summary="Endpoint para editar un color", tags=['Colores'])
def editar_color(color:Color, id_color:int):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    try:
        # Actualizar respuesta abierta en la base de datos
        query = "UPDATE colores SET nombre_color = %s, valor_hex = %s WHERE id_color = %s"
        evento_data = (color.nombre_color, color.valor_hex, id_color)
        cursor.execute(query, evento_data)
        connection.commit()
        return {
            'id_color': id_color,
            'nombre_color': color.nombre_color,
            'valor_hex': color.valor_hex
        }
    except mysql.connector.Error as err:
        # Manejar errores de la base de datos
        print(f"Error al actualizar el color en la base de datos: {err}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar el color")
    finally:
        cursor.close()
        connection.close()

@app.delete("/color/borrar/{id_color}", status_code=status.HTTP_200_OK, summary="Endpoint para borrar un color", tags=['Colores'])
def borrar_color(id_color: int):
    # Conectar a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Verificar si la repuesta existe
    cursor.execute("SELECT * FROM colores WHERE id_color =%s", (id_color,))
    aviso = cursor.fetchone()
    
    if not aviso:
        raise HTTPException(status_code=404, detail="Color no encontrado")

    # Eliminar el aviso de la base de datos
    cursor.execute("DELETE FROM colores WHERE id_color =%s", (id_color,))
    connection.commit()

    return JSONResponse(content={"message": "Color borrado correctamente", "id_color": id_color})
