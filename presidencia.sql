CREATE DATABASE presidencia;
USE presidencia;


-- USUARIOS (DONE) -------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    estado ENUM('0', '1') DEFAULT '1',
    permisos ENUM('0', '1') DEFAULT '0',
    salt VARCHAR(255) NOT NULL
);

-- PAGINA ---------------------------------------------------------
CREATE TABLE logo (
    id_logo INT AUTO_INCREMENT PRIMARY KEY,
    imagen VARCHAR(255) NOT NULL,
    ruta VARCHAR(255) NOT NULL
);

CREATE TABLE header (
    id_header INT AUTO_INCREMENT PRIMARY KEY,
    imagen VARCHAR(255) NOT NULL,
    ruta VARCHAR(255) NOT NULL
);

CREATE TABLE carrusel (
    id_imagen INT AUTO_INCREMENT PRIMARY KEY,
    imagen VARCHAR(255) NOT NULL,
    ruta VARCHAR(255) NOT NULL,
    estado ENUM('0', '1') DEFAULT '1',
    url VARCHAR(255) NOT NULL
);

CREATE TABLE ubicaciones (
    id_ubicacion INT AUTO_INCREMENT PRIMARY KEY,
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    lugar VARCHAR(255)
);

CREATE TABLE contactos (
    id_contactos INT AUTO_INCREMENT PRIMARY KEY,
    nombre_institucion TEXT,
    tipo_contacto ENUM('telefono','email'),
    contacto TEXT,
    horario TEXT
);

-- NOTICIAS ---------------------------------------------------------
CREATE TABLE noticias (
    id_noticia INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100),
    resumen TEXT,
    contenido longtext,
    imagen VARCHAR(255)
);
-- EVENTOS -- (CALENDARIO)-------------------------------------------------------
CREATE TABLE eventos (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(50),
    descripcion VARCHAR(100),
    fecha DATE,
    hora TIME
);

--ENCUESTAS-------------------------------------------------------

-- ENCUESTAS --
CREATE TABLE encuestas (
    id_encuesta INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(50)
);

-- PREGUNTAS --
CREATE TABLE preguntas (
    id_pregunta INT AUTO_INCREMENT PRIMARY KEY,
    id_encuesta INT,
    pregunta VARCHAR(100),
    pregunta_abierta ENUM('0','1') DEFAULT '0',
    pregunta_cerrada_multiple ENUM('0','1') DEFAULT '0',
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta)
);

-- OPCIONES --
CREATE TABLE opcion (
    id_opcion INT AUTO_INCREMENT PRIMARY KEY,
    id_pregunta INT,
    id_encuesta INT,
    opcion VARCHAR(100),
    FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta),
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta)
);

-- RESPUESTAS --

-- RESPUESTAS MULTIPLES --
CREATE TABLE respuesta_multiple_uno (
    id_respuesta INT AUTO_INCREMENT PRIMARY KEY,
    id_opcion INT,
    id_pregunta INT,
    id_encuesta INT,
    FOREIGN KEY (id_opcion) REFERENCES opcion(id_opcion),
    FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta),
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta)
);

-- RESPUESTAS SELECCION MULTIPLE -- 
CREATE TABLE respuesta_multiple_varios (
    id_respuesta INT AUTO_INCREMENT PRIMARY KEY,
    id_opcion INT,
    id_pregunta INT,
    id_encuesta INT,
    FOREIGN KEY (id_opcion) REFERENCES opcion(id_opcion),
    FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta),
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta)
);

-- RESPUESTAS ABIERTAS --
CREATE TABLE respuesta_abierta (
    id_respuesta_abierta INT AUTO_INCREMENT PRIMARY KEY,
    id_opcion INT,
    id_pregunta INT,
    id_encuesta INT,
    respuesta VARCHAR(200),
    FOREIGN KEY (id_opcion) REFERENCES opcion(id_opcion),
    FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta),
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta)
);



-- CHATBOT -------------------------------------------------------------------
CREATE TABLE bot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre TEXT,
    correo TEXT,
    actividad TEXT
);


-- DOCUMENTOS LEY GENERAL DE TRANSPARENCIA ------------------------------------
CREATE TABLE docs_ley_general (
    id_documento INT AUTO_INCREMENT PRIMARY KEY,
    articulo ENUM('69','70'),
    fraccion INT,
    sub_fraccion VARCHAR(255),
    desc_fraccion VARCHAR(255),
    año INT,
    tipo_resumen ENUM('Anual', 'Trimestral'),
    trimestre ENUM('1', '2', '3', '4'),
    ruta_archivo VARCHAR(50)
);
