-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 07-06-2024 a las 17:33:26
-- Versión del servidor: 10.4.28-MariaDB
-- Versión de PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `presidencia`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `articulos`
--

CREATE TABLE `articulos` (
  `id_articulo` int(11) NOT NULL,
  `num_articulo` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `articulos`
--

INSERT INTO `articulos` (`id_articulo`, `num_articulo`) VALUES
(4, 2),
(1, 69),
(2, 70);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `años`
--

CREATE TABLE `años` (
  `id_año` int(11) NOT NULL,
  `año` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `años`
--

INSERT INTO `años` (`id_año`, `año`) VALUES
(1, 2021),
(2, 2022),
(3, 2023),
(4, 2024);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bot`
--

CREATE TABLE `bot` (
  `id` int(11) NOT NULL,
  `nombre` text DEFAULT NULL,
  `correo` text DEFAULT NULL,
  `problema` text DEFAULT NULL,
  `area` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrusel`
--

CREATE TABLE `carrusel` (
  `id_imagen` int(11) NOT NULL,
  `imagen` varchar(255) NOT NULL,
  `ruta` varchar(255) NOT NULL,
  `estado` enum('0','1') DEFAULT '1',
  `url` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `carrusel`
--

INSERT INTO `carrusel` (`id_imagen`, `imagen`, `ruta`, `estado`, `url`) VALUES
(2, 'default.png', 'static/images/carrusel/', '0', 'ejemploinactivo.com'),
(4, 'logo_santiago.png', 'static/images/carrusel/', '0', 'eldiablo.com'),
(6, 'logo_santiago.png', 'static/images/carrusel/', '1', 'nm');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `colores`
--

CREATE TABLE `colores` (
  `id_color` int(11) NOT NULL,
  `nombre_color` varchar(15) NOT NULL,
  `valor_hex` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `colores`
--

INSERT INTO `colores` (`id_color`, `nombre_color`, `valor_hex`) VALUES
(1, 'primario', '#2596be'),
(2, 'secundario', '#085d94'),
(3, 'fondo', '#312b1d');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contactos`
--

CREATE TABLE `contactos` (
  `id_contactos` int(11) NOT NULL,
  `nombre_institucion` text DEFAULT NULL,
  `tipo_contacto` enum('telefono','email') DEFAULT NULL,
  `contacto` text DEFAULT NULL,
  `horario` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `contactos`
--

INSERT INTO `contactos` (`id_contactos`, `nombre_institucion`, `tipo_contacto`, `contacto`, `horario`) VALUES
(1, 'Presidencia Municipal', 'telefono', '01(775)7532914, 15, 16 Ext, 101 ', 'Horario de 8:30 AM a 4:30 PM'),
(2, 'Agua Potable', 'telefono', '01(775)7546459', 'Horario de 8:30 AM a 4:30 PM');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `documentos`
--

CREATE TABLE `documentos` (
  `id_documento` int(11) NOT NULL,
  `documento` varchar(200) DEFAULT NULL,
  `ruta` varchar(100) DEFAULT NULL,
  `trimestre` enum('1','2','3','4') DEFAULT NULL,
  `año` int(11) DEFAULT NULL,
  `id_fraccion` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `documentos`
--

INSERT INTO `documentos` (`id_documento`, `documento`, `ruta`, `trimestre`, `año`, `id_fraccion`) VALUES
(2, 'Checklist de metodos de la API.xlsx', 'static/documents/transparencia/69/2/2022', '2', 2022, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `encuestas`
--

CREATE TABLE `encuestas` (
  `id_encuesta` int(11) NOT NULL,
  `titulo` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `encuestas`
--

INSERT INTO `encuestas` (`id_encuesta`, `titulo`) VALUES
(1, 'Encuesta Economica');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `eventos`
--

CREATE TABLE `eventos` (
  `id_evento` int(11) NOT NULL,
  `titulo` varchar(50) DEFAULT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `hora` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `eventos`
--

INSERT INTO `eventos` (`id_evento`, `titulo`, `descripcion`, `fecha`, `hora`) VALUES
(1, 'Feria de Santiago Tulantepec', 'Feria de Santiago Tulantepec', '2024-06-14', '00:00:00'),
(3, 'string', 'string', '2024-06-06', '20:58:22');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `fracciones`
--

CREATE TABLE `fracciones` (
  `id_fraccion` int(11) NOT NULL,
  `fraccion` varchar(25) DEFAULT NULL,
  `descripcion` varchar(50) DEFAULT NULL,
  `area` varchar(75) DEFAULT NULL,
  `num_articulo` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `fracciones`
--

INSERT INTO `fracciones` (`id_fraccion`, `fraccion`, `descripcion`, `area`, `num_articulo`) VALUES
(1, '1', 'Marco normativo', 'Juridica', 69),
(2, '2', 'Estructura organica', 'Juridica', 69),
(3, '45', 'Catalogo y guia de archivos', 'Informatica', 69),
(4, '46', 'Sesiones organos consultivos', 'Secretario', 69),
(5, '1: A)', 'Plan de desarrollo', 'Innovacion', 70),
(6, '1: B)', 'Presupuesto de egresos', 'Contador', 70),
(8, '666', 'el diablo', 'satan', 69);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `logo`
--

CREATE TABLE `logo` (
  `id_logo` int(11) NOT NULL,
  `imagen` varchar(255) NOT NULL,
  `ruta` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `logo`
--

INSERT INTO `logo` (`id_logo`, `imagen`, `ruta`) VALUES
(1, 'logo_santiago.png', 'static/images/logos/');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `noticias`
--

CREATE TABLE `noticias` (
  `id_noticia` int(11) NOT NULL,
  `titulo` varchar(100) DEFAULT NULL,
  `contenido` longtext DEFAULT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `ruta` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `noticias`
--

INSERT INTO `noticias` (`id_noticia`, `titulo`, `contenido`, `imagen`, `ruta`) VALUES
(1, 'Reportan disparos vs alcadia de tlanchinol', 'Segun los informes preliminares, un grupo armado, a bordo de camionetas, disparo contra el inmueble, causando daños en las instalaciones', 'imagen.png', '/static/images/noticias'),
(2, 'HOSPITAL en doxey, listo antes de que amlo se vaya', 'Julio Menchaca Salazar, gobernador de Hiladgo, aseguro que el presidente de la Republica le ha encargado que el hosputal de especialidades del instituto Mexicano del Seguro Social.', 'imagen.png', '/static/images/noticias');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `opcion`
--

CREATE TABLE `opcion` (
  `id_opcion` int(11) NOT NULL,
  `id_pregunta` int(11) DEFAULT NULL,
  `id_encuesta` int(11) DEFAULT NULL,
  `opcion` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `opcion`
--

INSERT INTO `opcion` (`id_opcion`, `id_pregunta`, `id_encuesta`, `opcion`) VALUES
(1, 1, 1, 'Menos de $1,000'),
(2, 1, 1, 'Entre $1,000 y $3,000'),
(3, 1, 1, 'Entre $3,000 y $5,000'),
(4, 1, 1, 'Más de $5,000'),
(5, 2, 1, 'No ahorro'),
(6, 2, 1, 'Menos de $100'),
(7, 2, 1, 'Entre $100 y $500'),
(8, 2, 1, 'Mas de $500'),
(9, 3, 1, 'Inmuebles'),
(10, 3, 1, 'Acciones'),
(11, 3, 1, 'Bonos'),
(12, 3, 1, 'Fondos de inversión'),
(13, 3, 1, 'Criptomonedas'),
(14, 3, 1, 'No estoy interesado en invertir');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `organigrama`
--

CREATE TABLE `organigrama` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `comision` varchar(100) NOT NULL,
  `imagen` varchar(50) DEFAULT NULL,
  `ruta` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `preguntas`
--

CREATE TABLE `preguntas` (
  `id_pregunta` int(11) NOT NULL,
  `id_encuesta` int(11) DEFAULT NULL,
  `pregunta` varchar(100) DEFAULT NULL,
  `pregunta_abierta` enum('0','1') DEFAULT '0',
  `pregunta_cerrada_multiple` enum('0','1') DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `preguntas`
--

INSERT INTO `preguntas` (`id_pregunta`, `id_encuesta`, `pregunta`, `pregunta_abierta`, `pregunta_cerrada_multiple`) VALUES
(1, 1, '¿Cuál es su ingreso mensual aproximado?', '0', '0'),
(2, 1, '¿Cuánto ahorra mensualmente en promedio?', '0', '0'),
(3, 1, '¿En qué tipo de inversiones está interesado o actualmente invierte?', '0', '1'),
(4, 1, '¿Cuál es su mayor preocupación económica en este momento?', '1', '0');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `requisitos`
--

CREATE TABLE `requisitos` (
  `id_requisito` int(11) NOT NULL,
  `requisito` varchar(200) DEFAULT NULL,
  `id_tramite` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `requisitos`
--

INSERT INTO `requisitos` (`id_requisito`, `requisito`, `id_tramite`) VALUES
(1, 'Ultimo recibo de pago predial', 1),
(2, 'Credencial de INSEN, INAPAM, Pensionado o Jubilado.', 1),
(3, 'Escritura o titulo de propiedad', 1),
(4, 'ACTA DE NACIMIENTO Legible', 2),
(5, 'CONSTANCIA DE ESTUDIOS', 2),
(6, 'COMPROBANTE DE DOMICILIO', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `respuesta_abierta`
--

CREATE TABLE `respuesta_abierta` (
  `id_respuesta_abierta` int(11) NOT NULL,
  `id_pregunta` int(11) DEFAULT NULL,
  `id_encuesta` int(11) DEFAULT NULL,
  `respuesta` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `respuesta_cerrada`
--

CREATE TABLE `respuesta_cerrada` (
  `id_respuesta` int(11) NOT NULL,
  `id_opcion` int(11) DEFAULT NULL,
  `id_pregunta` int(11) DEFAULT NULL,
  `id_encuesta` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tramites_servicios`
--

CREATE TABLE `tramites_servicios` (
  `id_tramite` int(11) NOT NULL,
  `nombre` varchar(75) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tramites_servicios`
--

INSERT INTO `tramites_servicios` (`id_tramite`, `nombre`) VALUES
(1, 'Pago Predial'),
(2, 'Cartilla Militar');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ubicaciones`
--

CREATE TABLE `ubicaciones` (
  `id_ubicacion` int(11) NOT NULL,
  `latitud` decimal(10,8) DEFAULT NULL,
  `longitud` decimal(11,8) DEFAULT NULL,
  `lugar` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ubicaciones`
--

INSERT INTO `ubicaciones` (`id_ubicacion`, `latitud`, `longitud`, `lugar`) VALUES
(1, 20.03850760, -98.35464950, 'Presidencia de Santiago'),
(2, 22.04895730, -97.93843480, 'Tu casa'),
(4, 0.00000000, 0.00000000, 'string');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `area` varchar(70) NOT NULL,
  `estado` enum('0','1') DEFAULT '1',
  `permisos` enum('0','1','2') DEFAULT '0',
  `salt` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre`, `contrasena`, `area`, `estado`, `permisos`, `salt`) VALUES
(1, 'Dejah', 'nUpVTBeeoqxoRiR2cpc2uOpKhIsdTWWPjD2BPe1W1d8=', 'Comunicacion Social', '1', '1', 'zfrx+0VftIkJZx3i4QzM1w=='),
(2, 'Brallan', 'Nmi9GPcFwFHlKKsauJbOLxGQYPUq/cpZTMJFaJcb76A=', 'Juventud', '1', '1', 'nAxWd4IqbiBrsJ18ztUvnA=='),
(5, 'David', '6RDOhMG7Ul1pm5QSp/QNH3076IZd68m6TZUjH3iW5CI=', 'Algo', '1', '0', 'dtGj+/cq4imKAOeUtsq8FQ=='),
(6, 'Diego', 'ibBhBkQ+xLA8y11369CEckEYLFW8pmJSU/HG8VvqN4s=', 'Juventud', '0', '1', 'NGPtJL38vsqOgGl+j4rwfQ=='),
(7, 'Karla', 'amTs3A2unChoanNYPW8T+XS5Q8Ajg+rk4qCCK8ppydM=', 'Transparencia', '0', '2', 'u51ZbZaGCgAopcc+5OuXkA=='),
(8, 'Esmeralda', 'kaOv9bsPSXJAh6En7ccFtc8ksRoAoNrKD3x39NobEVM=', 'Algo', '1', '2', 'GJGWyDbu1/UZZPuXvOsJuQ==');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `articulos`
--
ALTER TABLE `articulos`
  ADD PRIMARY KEY (`id_articulo`),
  ADD UNIQUE KEY `num_articulo` (`num_articulo`);

--
-- Indices de la tabla `años`
--
ALTER TABLE `años`
  ADD PRIMARY KEY (`id_año`),
  ADD UNIQUE KEY `año` (`año`);

--
-- Indices de la tabla `bot`
--
ALTER TABLE `bot`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `carrusel`
--
ALTER TABLE `carrusel`
  ADD PRIMARY KEY (`id_imagen`);

--
-- Indices de la tabla `colores`
--
ALTER TABLE `colores`
  ADD PRIMARY KEY (`id_color`);

--
-- Indices de la tabla `contactos`
--
ALTER TABLE `contactos`
  ADD PRIMARY KEY (`id_contactos`);

--
-- Indices de la tabla `documentos`
--
ALTER TABLE `documentos`
  ADD PRIMARY KEY (`id_documento`),
  ADD KEY `año` (`año`),
  ADD KEY `id_fraccion` (`id_fraccion`);

--
-- Indices de la tabla `encuestas`
--
ALTER TABLE `encuestas`
  ADD PRIMARY KEY (`id_encuesta`);

--
-- Indices de la tabla `eventos`
--
ALTER TABLE `eventos`
  ADD PRIMARY KEY (`id_evento`);

--
-- Indices de la tabla `fracciones`
--
ALTER TABLE `fracciones`
  ADD PRIMARY KEY (`id_fraccion`),
  ADD KEY `num_articulo` (`num_articulo`);

--
-- Indices de la tabla `logo`
--
ALTER TABLE `logo`
  ADD PRIMARY KEY (`id_logo`);

--
-- Indices de la tabla `noticias`
--
ALTER TABLE `noticias`
  ADD PRIMARY KEY (`id_noticia`);

--
-- Indices de la tabla `opcion`
--
ALTER TABLE `opcion`
  ADD PRIMARY KEY (`id_opcion`),
  ADD KEY `id_pregunta` (`id_pregunta`),
  ADD KEY `id_encuesta` (`id_encuesta`);

--
-- Indices de la tabla `organigrama`
--
ALTER TABLE `organigrama`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `preguntas`
--
ALTER TABLE `preguntas`
  ADD PRIMARY KEY (`id_pregunta`),
  ADD KEY `id_encuesta` (`id_encuesta`);

--
-- Indices de la tabla `requisitos`
--
ALTER TABLE `requisitos`
  ADD PRIMARY KEY (`id_requisito`),
  ADD KEY `id_tramite` (`id_tramite`);

--
-- Indices de la tabla `respuesta_abierta`
--
ALTER TABLE `respuesta_abierta`
  ADD PRIMARY KEY (`id_respuesta_abierta`),
  ADD KEY `id_pregunta` (`id_pregunta`),
  ADD KEY `id_encuesta` (`id_encuesta`);

--
-- Indices de la tabla `respuesta_cerrada`
--
ALTER TABLE `respuesta_cerrada`
  ADD PRIMARY KEY (`id_respuesta`),
  ADD KEY `id_opcion` (`id_opcion`),
  ADD KEY `id_pregunta` (`id_pregunta`),
  ADD KEY `id_encuesta` (`id_encuesta`);

--
-- Indices de la tabla `tramites_servicios`
--
ALTER TABLE `tramites_servicios`
  ADD PRIMARY KEY (`id_tramite`);

--
-- Indices de la tabla `ubicaciones`
--
ALTER TABLE `ubicaciones`
  ADD PRIMARY KEY (`id_ubicacion`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `articulos`
--
ALTER TABLE `articulos`
  MODIFY `id_articulo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `años`
--
ALTER TABLE `años`
  MODIFY `id_año` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `bot`
--
ALTER TABLE `bot`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `carrusel`
--
ALTER TABLE `carrusel`
  MODIFY `id_imagen` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `colores`
--
ALTER TABLE `colores`
  MODIFY `id_color` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `contactos`
--
ALTER TABLE `contactos`
  MODIFY `id_contactos` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `documentos`
--
ALTER TABLE `documentos`
  MODIFY `id_documento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `encuestas`
--
ALTER TABLE `encuestas`
  MODIFY `id_encuesta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `eventos`
--
ALTER TABLE `eventos`
  MODIFY `id_evento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `fracciones`
--
ALTER TABLE `fracciones`
  MODIFY `id_fraccion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `logo`
--
ALTER TABLE `logo`
  MODIFY `id_logo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `noticias`
--
ALTER TABLE `noticias`
  MODIFY `id_noticia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `opcion`
--
ALTER TABLE `opcion`
  MODIFY `id_opcion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `organigrama`
--
ALTER TABLE `organigrama`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `preguntas`
--
ALTER TABLE `preguntas`
  MODIFY `id_pregunta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `requisitos`
--
ALTER TABLE `requisitos`
  MODIFY `id_requisito` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `respuesta_abierta`
--
ALTER TABLE `respuesta_abierta`
  MODIFY `id_respuesta_abierta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `respuesta_cerrada`
--
ALTER TABLE `respuesta_cerrada`
  MODIFY `id_respuesta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tramites_servicios`
--
ALTER TABLE `tramites_servicios`
  MODIFY `id_tramite` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `ubicaciones`
--
ALTER TABLE `ubicaciones`
  MODIFY `id_ubicacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `documentos`
--
ALTER TABLE `documentos`
  ADD CONSTRAINT `documentos_ibfk_1` FOREIGN KEY (`año`) REFERENCES `años` (`año`) ON DELETE CASCADE,
  ADD CONSTRAINT `documentos_ibfk_2` FOREIGN KEY (`id_fraccion`) REFERENCES `fracciones` (`id_fraccion`) ON DELETE CASCADE;

--
-- Filtros para la tabla `fracciones`
--
ALTER TABLE `fracciones`
  ADD CONSTRAINT `fracciones_ibfk_1` FOREIGN KEY (`num_articulo`) REFERENCES `articulos` (`num_articulo`) ON DELETE CASCADE;

--
-- Filtros para la tabla `opcion`
--
ALTER TABLE `opcion`
  ADD CONSTRAINT `opcion_ibfk_1` FOREIGN KEY (`id_pregunta`) REFERENCES `preguntas` (`id_pregunta`) ON DELETE CASCADE,
  ADD CONSTRAINT `opcion_ibfk_2` FOREIGN KEY (`id_encuesta`) REFERENCES `encuestas` (`id_encuesta`) ON DELETE CASCADE;

--
-- Filtros para la tabla `preguntas`
--
ALTER TABLE `preguntas`
  ADD CONSTRAINT `preguntas_ibfk_1` FOREIGN KEY (`id_encuesta`) REFERENCES `encuestas` (`id_encuesta`) ON DELETE CASCADE;

--
-- Filtros para la tabla `requisitos`
--
ALTER TABLE `requisitos`
  ADD CONSTRAINT `requisitos_ibfk_1` FOREIGN KEY (`id_tramite`) REFERENCES `tramites_servicios` (`id_tramite`) ON DELETE CASCADE;

--
-- Filtros para la tabla `respuesta_abierta`
--
ALTER TABLE `respuesta_abierta`
  ADD CONSTRAINT `respuesta_abierta_ibfk_1` FOREIGN KEY (`id_pregunta`) REFERENCES `preguntas` (`id_pregunta`) ON DELETE CASCADE,
  ADD CONSTRAINT `respuesta_abierta_ibfk_2` FOREIGN KEY (`id_encuesta`) REFERENCES `encuestas` (`id_encuesta`) ON DELETE CASCADE;

--
-- Filtros para la tabla `respuesta_cerrada`
--
ALTER TABLE `respuesta_cerrada`
  ADD CONSTRAINT `respuesta_cerrada_ibfk_1` FOREIGN KEY (`id_opcion`) REFERENCES `opcion` (`id_opcion`) ON DELETE CASCADE,
  ADD CONSTRAINT `respuesta_cerrada_ibfk_2` FOREIGN KEY (`id_pregunta`) REFERENCES `preguntas` (`id_pregunta`) ON DELETE CASCADE,
  ADD CONSTRAINT `respuesta_cerrada_ibfk_3` FOREIGN KEY (`id_encuesta`) REFERENCES `encuestas` (`id_encuesta`) ON DELETE CASCADE;

DELIMITER $$
--
-- Eventos
--
CREATE DEFINER=`root`@`localhost` EVENT `add_new_year_event` ON SCHEDULE EVERY 1 YEAR STARTS '2025-01-01 00:00:00' ON COMPLETION NOT PRESERVE ENABLE DO INSERT INTO años (año)
  SELECT YEAR(CURDATE()) + 1
  WHERE NOT EXISTS (SELECT 1 FROM años WHERE año = YEAR(CURDATE()) + 1)$$

DELIMITER ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
