CREATE DATABASE presidencia;
USE presidencia;


-- USUARIOS (DONE JS) -------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    area VARCHAR(70) NOT NULL,
    estado ENUM('0', '1') DEFAULT '1',
    permisos ENUM('0', '1','2') DEFAULT '0',
    salt VARCHAR(255) NOT NULL
);


-- PAGINA (DONE JS) ---------------------------------------------------------
CREATE TABLE logo (
    id_logo INT AUTO_INCREMENT PRIMARY KEY,
    imagen VARCHAR(255) NOT NULL,
    ruta VARCHAR(255) NOT NULL
);

INSERT INTO logo (imagen,ruta) VALUES
('default_logo.png','static/images/logo/');



-- COLORES (DONE JS) ------------------------------------------------------------------
CREATE TABLE colores (
    id_color INT AUTO_INCREMENT PRIMARY KEY,
    nombre_color VARCHAR(15) NOT NULL,
    valor_hex VARCHAR(10) NOT NULL
);

INSERT INTO colores (nombre_color, valor_hex) VALUES 
('primario','#2596be'),
('secundario','#085d94'),
('fondo','#312b1d');

-- CREATE TABLE header (
--     id_header INT AUTO_INCREMENT PRIMARY KEY,
--     imagen VARCHAR(255) NOT NULL,
--     ruta VARCHAR(255) NOT NULL
-- );

-- INSERT INTO header (imagen,ruta) VALUES
-- ('default_header.png','static/images/header/');


-- CARRUSEL (DONE JS) --------------------------------
CREATE TABLE carrusel (
    id_imagen INT AUTO_INCREMENT PRIMARY KEY,
    imagen VARCHAR(255) NOT NULL,
    ruta VARCHAR(255) NOT NULL,
    estado ENUM('0', '1') DEFAULT '1',
    url VARCHAR(255) NOT NULL
);

INSERT INTO carrusel (imagen, ruta, estado, url) VALUES
('imagen.png','static/images/carrusel','1','ejemplo.com'),
('imagen.png','static/images/carrusel','0','ejemploinactivo.com'),
('imagen2.png','static/images/carrusel','1','ejemploactivo.com');

-- UBICACIONES (DONE JS) ------
CREATE TABLE ubicaciones (
    id_ubicacion INT AUTO_INCREMENT PRIMARY KEY,
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    lugar VARCHAR(255)
);

INSERT INTO ubicaciones (latitud,longitud,lugar) VALUES
(20.0385076,-98.3546495,'Presidencia de Santiago'),
(22.0489573,-97.9384348,'Tu casa'),
(21.8745458,-98.2648724,'La tienda');



CREATE TABLE contactos (
    id_contactos INT AUTO_INCREMENT PRIMARY KEY,
    nombre_institucion TEXT,
    tipo_contacto ENUM('telefono','email'),
    contacto TEXT,
    horario TEXT
);

INSERT INTO contactos (nombre_institucion, tipo_contacto, contacto, horario) VALUES
('Presidencia Municipal','telefono','01(775)7532914, 15, 16 Ext, 101 ','Horario de 8:30 AM a 4:30 PM'),
('Agua Potable','telefono','01(775)7546459','Horario de 8:30 AM a 4:30 PM');

-- NOTICIAS (DONE JS) ---------------------------------------------------------
CREATE TABLE noticias (
    id_noticia INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100),
    contenido longtext,
    imagen VARCHAR(255),
    ruta VARCHAR(255)
);

INSERT INTO noticias (titulo, contenido, imagen, ruta) VALUES
('Reportan disparos vs alcadia de tlanchinol','Segun los informes preliminares, un grupo armado, a bordo de camionetas, disparo contra el inmueble, causando daños en las instalaciones','imagen.png','/static/images/noticias'),
('HOSPITAL en doxey, listo antes de que amlo se vaya','Julio Menchaca Salazar, gobernador de Hiladgo, aseguro que el presidente de la Republica le ha encargado que el hosputal de especialidades del instituto Mexicano del Seguro Social.','imagen.png','/static/images/noticias');

-- EVENTOS -- (CALENDARIO) (DONE JS) -------------------------------------------------------
CREATE TABLE eventos (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(50),
    descripcion VARCHAR(100),
    fecha DATE,
    hora TIME
);

INSERT INTO eventos(titulo, descripcion, fecha, hora) VALUES
('Feria de Santiago Tulantepec', 'Feria de Santiago Tulantepec', '2024-06-14', '00:00:00');

-- ENCUESTAS --
CREATE TABLE encuestas (
    id_encuesta INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(50)
);

INSERT INTO encuestas (titulo) VALUES
('Encuesta Economica');

-- PREGUNTAS --
CREATE TABLE preguntas (
    id_pregunta INT AUTO_INCREMENT PRIMARY KEY,
    id_encuesta INT,
    pregunta VARCHAR(100),
    pregunta_abierta ENUM('0','1') DEFAULT '0',
    pregunta_cerrada_multiple ENUM('0','1') DEFAULT '0',
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
);

-- Inserción de la pregunta
INSERT INTO preguntas (id_encuesta, pregunta, pregunta_abierta, pregunta_cerrada_multiple) VALUES
(1, '¿Cuál es su ingreso mensual aproximado?', '0', '0'),
(1, '¿Cuánto ahorra mensualmente en promedio?', '0', '0'),
(1, '¿En qué tipo de inversiones está interesado o actualmente invierte?', '0', '1'),
(1, '¿Cuál es su mayor preocupación económica en este momento?', '1', '0');

-- OPCIONES --
CREATE TABLE opcion (
    id_opcion INT AUTO_INCREMENT PRIMARY KEY,
    id_pregunta INT,
    id_encuesta INT,
    opcion VARCHAR(100),
    FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
);

INSERT INTO opcion (id_pregunta, id_encuesta, opcion) VALUES
(1, 1, 'Menos de $1,000'),
(1, 1, 'Entre $1,000 y $3,000'),
(1, 1, 'Entre $3,000 y $5,000'),
(1, 1, 'Más de $5,000');

INSERT INTO opcion (id_pregunta, id_encuesta, opcion) VALUES
(2, 1, 'No ahorro'),
(2, 1, 'Menos de $100'),
(2, 1, 'Entre $100 y $500'),
(2, 1, 'Mas de $500');

INSERT INTO opcion (id_pregunta, id_encuesta, opcion) VALUES
(3, 1, 'Inmuebles'),
(3, 1, 'Acciones'),
(3, 1, 'Bonos'),
(3, 1, 'Fondos de inversión'),
(3, 1, 'Criptomonedas'),
(3, 1, 'No estoy interesado en invertir');

-- RESPUESTAS --

-- RESPUESTAS MULTIPLES 
CREATE TABLE respuesta_cerrada (
    id_respuesta INT AUTO_INCREMENT PRIMARY KEY,
    id_opcion INT,
    id_pregunta INT,
    id_encuesta INT,
    FOREIGN KEY (id_opcion) REFERENCES opcion(id_opcion) ON DELETE CASCADE,
    FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
);

-- RESPUESTAS ABIERTAS 
CREATE TABLE respuesta_abierta (
    id_respuesta_abierta INT AUTO_INCREMENT PRIMARY KEY,
    id_pregunta INT,
    id_encuesta INT,
    respuesta VARCHAR(200),
    FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
    FOREIGN KEY (id_encuesta) REFERENCES encuestas(id_encuesta) ON DELETE CASCADE
);

-- CHATBOT 
CREATE TABLE bot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre TEXT,
    correo TEXT,
    problema TEXT,
    area TEXT
);


-- LEY DE TRANSPARENCIA (DOCUMENTOS)

CREATE TABLE articulos(
    id_articulo INT AUTO_INCREMENT PRIMARY KEY,
    num_articulo INT UNIQUE
);

INSERT INTO articulos (num_articulo) VALUES
(69),
(70);

CREATE TABLE fracciones(
    id_fraccion INT AUTO_INCREMENT PRIMARY KEY,
    fraccion VARCHAR(25),
    descripcion VARCHAR(50),
    area VARCHAR(75),
    num_articulo INT,
    FOREIGN KEY (num_articulo) REFERENCES articulos(num_articulo) ON DELETE CASCADE
);

INSERT INTO fracciones (fraccion, descripcion, area, num_articulo) VALUES
('1', 'Marco normativo', 'Juridica', 69),
('2', 'Estructura organica', 'Juridica', 69),
('45', 'Catalogo y guia de archivos', 'Informatica', 69),
('46', 'Sesiones organos consultivos', 'Secretario', 69),
('1: A)', 'Plan de desarrollo', 'Innovacion', 70),
('1: B)', 'Presupuesto de egresos', 'Contador', 70);

-- Habilitar el programador de eventos
SET GLOBAL event_scheduler = ON;

-- Crear la tabla años si no existe
CREATE TABLE IF NOT EXISTS años (
    id_año INT AUTO_INCREMENT PRIMARY KEY,
    año INT UNIQUE
);

-- Insertar los años iniciales si no existen
INSERT IGNORE INTO años (año) VALUES
(2021),
(2022),
(2023),
(2024);

-- Crear el evento para añadir automáticamente un nuevo año cada 1 de enero
CREATE EVENT IF NOT EXISTS add_new_year_event
ON SCHEDULE EVERY 1 YEAR
STARTS '2025-01-01 00:00:00'
DO
  INSERT INTO años (año)
  SELECT YEAR(CURDATE()) + 1
  WHERE NOT EXISTS (SELECT 1 FROM años WHERE año = YEAR(CURDATE()) + 1);


CREATE TABLE documentos(
    id_documento INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(200),
    ruta VARCHAR(100),
    trimestre ENUM('1','2','3','4'),
    año INT,
    id_fraccion INT,
    FOREIGN KEY (año) REFERENCES años(año) ON DELETE CASCADE,
    FOREIGN KEY (id_fraccion) REFERENCES fracciones(id_fraccion) ON DELETE CASCADE
);

INSERT INTO documentos (documento, ruta, trimestre, año, id_fraccion) VALUES
('a69_f01.xlsx','1',2024,1),
('a69_f02.xlsx','1',2024,2),
('a69_f45.xlsx','1',2024,3),
('a69_f46.xlsx','1',2024,4),
('a70_f01_a1.xlsx','1',2024,5),
('a70_f01_b1.xlsx','1',2024,6);

CREATE TABLE tramites_servicios (
    id_tramite INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(75)
);

INSERT INTO tramites_servicios(nombre) VALUES
('Pago Predial'),
('Cartilla Militar');

CREATE TABLE requisitos(
    id_requisito INT AUTO_INCREMENT PRIMARY KEY,
    requisito VARCHAR(200),
    id_tramite INT,
    FOREIGN KEY (id_tramite) REFERENCES tramites_servicios(id_tramite) ON DELETE CASCADE
);

INSERT INTO requisitos(requisito, id_tramite) VALUES
('Ultimo recibo de pago predial',1),
('Credencial de INSEN, INAPAM, Pensionado o Jubilado.',1),
('Escritura o titulo de propiedad',1),
('ACTA DE NACIMIENTO Legible',2),
('CONSTANCIA DE ESTUDIOS',2),
('COMPROBANTE DE DOMICILIO',2);

CREATE TABLE organigrama(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    comision VARCHAR(100) NOT NULL,
    imagen VARCHAR(50),
    ruta VARCHAR(50)
);
-- Falta corregir / comprobar 
-- probar si la logica de los docs funciona
-- probar si la logica de las encuestas funciona
-- hacer nueva pagina para banco de respuestas (OPCIONAL)