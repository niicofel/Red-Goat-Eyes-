-- ============================================================
-- 01 · ESTRUCTURA
-- Crea las 21 tablas con sus claves, restricciones e indices.
-- El orden importa: primero las tablas de catalogo y luego las
-- que dependen de ellas por clave foranea.
-- ============================================================
-- ---------------- Provincias y ciudades del Ecuador ----------------
CREATE TABLE provincia (
    id_provincia  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre        VARCHAR(60) NOT NULL,

    CONSTRAINT uq_provincia_nombre UNIQUE (nombre),
    CONSTRAINT chk_provincia_nombre CHECK (LENGTH(TRIM(nombre)) >= 3)
);

COMMENT ON TABLE provincia IS 'Catalogo de las provincias del Ecuador';


CREATE TABLE ciudad (
    id_ciudad         INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_provincia      INT NOT NULL,
    nombre            VARCHAR(60) NOT NULL,
    costo_envio_base  NUMERIC(10,2) NOT NULL DEFAULT 0,

    CONSTRAINT fk_ciudad_provincia
        FOREIGN KEY (id_provincia) REFERENCES provincia (id_provincia)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_ciudad_provincia_nombre UNIQUE (id_provincia, nombre),
    CONSTRAINT chk_ciudad_nombre CHECK (LENGTH(TRIM(nombre)) >= 3),
    CONSTRAINT chk_ciudad_costo  CHECK (costo_envio_base >= 0)
);

COMMENT ON TABLE ciudad IS 'Ciudades. Sustituye al campo de texto libre del formulario de contacto';

CREATE INDEX idx_ciudad_provincia ON ciudad (id_provincia);



-- ---------------- Categorias del catalogo ----------------
CREATE TABLE categoria (
    id_categoria    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          VARCHAR(50)  NOT NULL,
    slug            VARCHAR(50)  NOT NULL,
    descripcion     TEXT,
    imagen_portada  VARCHAR(255) NOT NULL,
    activa          BOOLEAN      NOT NULL DEFAULT TRUE,
    fecha_creacion  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_categoria_nombre UNIQUE (nombre),
    CONSTRAINT uq_categoria_slug   UNIQUE (slug),
    CONSTRAINT chk_categoria_nombre CHECK (LENGTH(TRIM(nombre)) >= 3),
    CONSTRAINT chk_categoria_slug   CHECK (slug ~ '^[a-z0-9-]+$')
);

COMMENT ON TABLE categoria IS 'Hoodies, Pantalones y Accesorios';



-- ---------------- Tallas disponibles ----------------
-- El campo orden sirve para mostrarlas de menor a mayor
CREATE TABLE talla (
    id_talla     INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo       VARCHAR(5)  NOT NULL,
    descripcion  VARCHAR(30) NOT NULL,
    orden        SMALLINT    NOT NULL,

    CONSTRAINT uq_talla_codigo UNIQUE (codigo),
    CONSTRAINT uq_talla_orden  UNIQUE (orden),
    CONSTRAINT chk_talla_orden CHECK (orden > 0)
);

COMMENT ON TABLE talla IS 'Catalogo de tallas. En esta version se siembra solo la talla U (unica)';



-- ---------------- Productos ----------------
-- El stock NO esta aqui: esta en producto_talla
CREATE TABLE producto (
    id_producto       INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_categoria      INT NOT NULL,
    codigo            VARCHAR(20)  NOT NULL,
    nombre            VARCHAR(120) NOT NULL,
    descripcion       TEXT         NOT NULL,
    precio            NUMERIC(10,2) NOT NULL,
    precio_oferta     NUMERIC(10,2),
    imagen_principal  VARCHAR(255) NOT NULL,
    material          VARCHAR(80),
    genero            VARCHAR(10)  NOT NULL DEFAULT 'Unisex',
    activo            BOOLEAN      NOT NULL DEFAULT TRUE,
    destacado         BOOLEAN      NOT NULL DEFAULT FALSE,
    fecha_creacion    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_producto_codigo UNIQUE (codigo),

    CONSTRAINT chk_producto_codigo CHECK (codigo ~ '^RGE-[A-Z]{3}-[0-9]{3}$'),
    CONSTRAINT chk_producto_nombre CHECK (LENGTH(TRIM(nombre)) >= 3),
    CONSTRAINT chk_producto_descripcion CHECK (LENGTH(TRIM(descripcion)) >= 10),

    CONSTRAINT chk_producto_precio CHECK (precio > 0),

    CONSTRAINT chk_producto_oferta CHECK (
        precio_oferta IS NULL
        OR (precio_oferta > 0 AND precio_oferta < precio)
    ),

    CONSTRAINT chk_producto_genero CHECK (genero IN ('Hombre', 'Mujer', 'Unisex'))
);

COMMENT ON TABLE producto IS 'Ficha de cada prenda. 24 productos reales del catalogo';

CREATE INDEX idx_producto_categoria ON producto (id_categoria);
CREATE INDEX idx_producto_activo    ON producto (activo) WHERE activo = TRUE;



-- ---------------- Inventario por talla ----------------
-- Tabla puente. Cada fila es un producto en una talla, con su stock
CREATE TABLE producto_talla (
    id_producto_talla  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_producto        INT NOT NULL,
    id_talla           INT NOT NULL,
    stock              INT NOT NULL DEFAULT 0,
    stock_minimo       INT NOT NULL DEFAULT 3,

    CONSTRAINT fk_producto_talla_producto
        FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_producto_talla_talla
        FOREIGN KEY (id_talla) REFERENCES talla (id_talla)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_producto_talla UNIQUE (id_producto, id_talla),

    CONSTRAINT chk_producto_talla_stock CHECK (stock >= 0),
    CONSTRAINT chk_producto_talla_minimo CHECK (stock_minimo >= 0)
);

COMMENT ON TABLE producto_talla IS 'Tabla puente N:M entre producto y talla. Aqui vive el stock';

CREATE INDEX idx_producto_talla_producto ON producto_talla (id_producto);
CREATE INDEX idx_producto_talla_talla    ON producto_talla (id_talla);



-- ---------------- Imagenes de los productos ----------------
CREATE TABLE imagen_producto (
    id_imagen    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_producto  INT NOT NULL,
    url          VARCHAR(255) NOT NULL,

    alt_text     VARCHAR(150) NOT NULL,
    orden        SMALLINT     NOT NULL DEFAULT 1,

    CONSTRAINT fk_imagen_producto
        FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT uq_imagen_producto_orden UNIQUE (id_producto, orden),
    CONSTRAINT chk_imagen_alt CHECK (LENGTH(TRIM(alt_text)) >= 5),
    CONSTRAINT chk_imagen_orden CHECK (orden > 0)
);

COMMENT ON TABLE imagen_producto IS 'Galeria 1:N por producto con texto alternativo obligatorio';

CREATE INDEX idx_imagen_producto ON imagen_producto (id_producto);



-- ---------------- Usuarios y credenciales ----------------
-- Guarda el hash de la contrasena, nunca la contrasena real
CREATE TABLE usuario (
    id_usuario      INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           VARCHAR(120) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    rol             VARCHAR(15)  NOT NULL DEFAULT 'cliente',
    activo          BOOLEAN      NOT NULL DEFAULT TRUE,
    fecha_registro  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso   TIMESTAMP,

    CONSTRAINT uq_usuario_email UNIQUE (email),

    CONSTRAINT chk_usuario_email CHECK (
        email ~* '^[^\s@]+@[^\s@]+\.[^\s@]{2,}$'
    ),

    CONSTRAINT chk_usuario_password CHECK (LENGTH(password_hash) >= 20),

    CONSTRAINT chk_usuario_rol CHECK (rol IN ('cliente', 'administrador')),

    CONSTRAINT chk_usuario_acceso CHECK (
        ultimo_acceso IS NULL OR ultimo_acceso >= fecha_registro
    )
);

COMMENT ON TABLE usuario IS 'Credenciales y rol. Tabla base de la herencia cliente/administrador';

CREATE INDEX idx_usuario_rol ON usuario (rol);



-- ---------------- Datos de cliente ----------------
-- Su clave primaria es tambien clave foranea hacia usuario
CREATE TABLE cliente (
    id_cliente        INT PRIMARY KEY,
    nombres           VARCHAR(60) NOT NULL,
    apellidos         VARCHAR(60) NOT NULL,
    cedula            VARCHAR(10),
    telefono          VARCHAR(15),
    fecha_nacimiento  DATE,
    id_ciudad         INT,

    CONSTRAINT fk_cliente_usuario
        FOREIGN KEY (id_cliente) REFERENCES usuario (id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_cliente_ciudad
        FOREIGN KEY (id_ciudad) REFERENCES ciudad (id_ciudad)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_cliente_cedula UNIQUE (cedula),

    CONSTRAINT chk_cliente_nombres   CHECK (LENGTH(TRIM(nombres)) >= 3),
    CONSTRAINT chk_cliente_apellidos CHECK (LENGTH(TRIM(apellidos)) >= 3),

    CONSTRAINT chk_cliente_cedula CHECK (cedula IS NULL OR cedula ~ '^[0-9]{10}$'),

    CONSTRAINT chk_cliente_telefono CHECK (
        telefono IS NULL OR telefono ~ '^[0-9+\-\s]{7,15}$'
    ),

    CONSTRAINT chk_cliente_nacimiento CHECK (
        fecha_nacimiento IS NULL OR fecha_nacimiento < CURRENT_DATE
    )
);

COMMENT ON TABLE cliente IS 'Especializacion 1:1 de usuario. PK = FK a usuario';

CREATE INDEX idx_cliente_ciudad ON cliente (id_ciudad);



-- ---------------- Datos de administrador ----------------
CREATE TABLE administrador (
    id_administrador  INT PRIMARY KEY,
    nombres           VARCHAR(60) NOT NULL,
    apellidos         VARCHAR(60) NOT NULL,
    cargo             VARCHAR(50) NOT NULL DEFAULT 'Operador',
    nivel_acceso      SMALLINT    NOT NULL DEFAULT 1,

    CONSTRAINT fk_administrador_usuario
        FOREIGN KEY (id_administrador) REFERENCES usuario (id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_admin_nombres   CHECK (LENGTH(TRIM(nombres)) >= 3),
    CONSTRAINT chk_admin_apellidos CHECK (LENGTH(TRIM(apellidos)) >= 3),
    CONSTRAINT chk_admin_nivel     CHECK (nivel_acceso BETWEEN 1 AND 3)
);

COMMENT ON TABLE administrador IS 'Especializacion 1:1 de usuario. PK = FK a usuario';



-- ---------------- Direcciones de entrega ----------------
CREATE TABLE direccion_envio (
    id_direccion      INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente        INT NOT NULL,
    id_ciudad         INT NOT NULL,
    calle_principal   VARCHAR(120) NOT NULL,
    calle_secundaria  VARCHAR(120),
    numeracion        VARCHAR(20),
    referencia        TEXT,
    codigo_postal     VARCHAR(10),
    es_principal      BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_direccion_cliente
        FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_direccion_ciudad
        FOREIGN KEY (id_ciudad) REFERENCES ciudad (id_ciudad)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT chk_direccion_calle CHECK (LENGTH(TRIM(calle_principal)) >= 5),

    CONSTRAINT chk_direccion_postal CHECK (
        codigo_postal IS NULL OR codigo_postal ~ '^[0-9]{6}$'
    )
);

COMMENT ON TABLE direccion_envio IS 'Direcciones de entrega del cliente. Se captura en pago.html';

CREATE INDEX idx_direccion_cliente ON direccion_envio (id_cliente);
CREATE INDEX idx_direccion_ciudad  ON direccion_envio (id_ciudad);



-- ---------------- Estados y metodos de pago ----------------
CREATE TABLE estado_pedido (
    id_estado    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre       VARCHAR(20) NOT NULL,
    descripcion  VARCHAR(100),
    orden        SMALLINT NOT NULL,

    CONSTRAINT uq_estado_nombre UNIQUE (nombre),
    CONSTRAINT uq_estado_orden  UNIQUE (orden),
    CONSTRAINT chk_estado_orden CHECK (orden > 0)
);

COMMENT ON TABLE estado_pedido IS 'Pendiente, Pagado, En preparacion, Enviado, Entregado, Cancelado';


CREATE TABLE metodo_pago (
    id_metodo  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre     VARCHAR(40) NOT NULL,
    activo     BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_metodo_nombre UNIQUE (nombre),
    CONSTRAINT chk_metodo_nombre CHECK (LENGTH(TRIM(nombre)) >= 3)
);

COMMENT ON TABLE metodo_pago IS 'Los 4 metodos que ofrece pago.html';



-- ---------------- Pedidos ----------------
-- Guarda subtotal, IVA y total a proposito, para conservar el historial
CREATE TABLE pedido (
    id_pedido       INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_pedido   VARCHAR(20) NOT NULL,
    id_cliente      INT NOT NULL,
    id_direccion    INT NOT NULL,
    id_estado       INT NOT NULL DEFAULT 1,
    id_metodo_pago  INT,
    fecha_pedido    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    subtotal        NUMERIC(10,2) NOT NULL DEFAULT 0,
    iva             NUMERIC(10,2) NOT NULL DEFAULT 0,
    costo_envio     NUMERIC(10,2) NOT NULL DEFAULT 0,
    total           NUMERIC(10,2) NOT NULL DEFAULT 0,
    observaciones   TEXT,

    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_pedido_direccion
        FOREIGN KEY (id_direccion) REFERENCES direccion_envio (id_direccion)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_pedido_estado
        FOREIGN KEY (id_estado) REFERENCES estado_pedido (id_estado)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_pedido_metodo
        FOREIGN KEY (id_metodo_pago) REFERENCES metodo_pago (id_metodo)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_pedido_codigo UNIQUE (codigo_pedido),

    CONSTRAINT chk_pedido_codigo CHECK (codigo_pedido ~ '^RGE-[0-9]{4}-[0-9]{4}$'),

    CONSTRAINT chk_pedido_subtotal CHECK (subtotal    >= 0),
    CONSTRAINT chk_pedido_iva      CHECK (iva         >= 0),
    CONSTRAINT chk_pedido_envio    CHECK (costo_envio >= 0),
    CONSTRAINT chk_pedido_total    CHECK (total       >= 0),

    CONSTRAINT chk_pedido_coherencia CHECK (total >= subtotal)
);

COMMENT ON TABLE pedido IS 'Cabecera de la orden. Los totales los mantiene un trigger';

CREATE INDEX idx_pedido_cliente ON pedido (id_cliente);
CREATE INDEX idx_pedido_estado  ON pedido (id_estado);
CREATE INDEX idx_pedido_fecha   ON pedido (fecha_pedido);



-- ---------------- Lineas de cada pedido ----------------
-- El precio se congela aqui, para que el pedido no cambie despues
CREATE TABLE detalle_pedido (
    id_detalle         INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pedido          INT NOT NULL,
    id_producto_talla  INT NOT NULL,
    cantidad           INT NOT NULL,

    precio_unitario    NUMERIC(10,2) NOT NULL,
    descuento          NUMERIC(10,2) NOT NULL DEFAULT 0,

    subtotal_linea     NUMERIC(10,2)
        GENERATED ALWAYS AS ((cantidad * precio_unitario) - descuento) STORED,

    CONSTRAINT fk_detalle_pedido
        FOREIGN KEY (id_pedido) REFERENCES pedido (id_pedido)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_detalle_producto_talla
        FOREIGN KEY (id_producto_talla) REFERENCES producto_talla (id_producto_talla)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_detalle_pedido_producto UNIQUE (id_pedido, id_producto_talla),

    CONSTRAINT chk_detalle_cantidad  CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_precio    CHECK (precio_unitario > 0),
    CONSTRAINT chk_detalle_descuento CHECK (
        descuento >= 0 AND descuento < (cantidad * precio_unitario)
    )
);

COMMENT ON TABLE detalle_pedido IS 'Tabla puente N:M con atributos. Precio congelado al comprar';

CREATE INDEX idx_detalle_pedido   ON detalle_pedido (id_pedido);
CREATE INDEX idx_detalle_producto ON detalle_pedido (id_producto_talla);



-- ---------------- Carrito guardado ----------------
CREATE TABLE carrito (
    id_carrito           INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente           INT NOT NULL,
    fecha_creacion       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_carrito_cliente
        FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT uq_carrito_cliente UNIQUE (id_cliente),
    CONSTRAINT chk_carrito_fechas CHECK (fecha_actualizacion >= fecha_creacion)
);

COMMENT ON TABLE carrito IS 'Un carrito activo por cliente. El UNIQUE sobre la FK fuerza el 1:1';


CREATE TABLE carrito_item (
    id_item            INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_carrito         INT NOT NULL,
    id_producto_talla  INT NOT NULL,
    cantidad           INT NOT NULL,

    CONSTRAINT fk_carrito_item_carrito
        FOREIGN KEY (id_carrito) REFERENCES carrito (id_carrito)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_carrito_item_producto_talla
        FOREIGN KEY (id_producto_talla) REFERENCES producto_talla (id_producto_talla)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_carrito_item UNIQUE (id_carrito, id_producto_talla),
    CONSTRAINT chk_carrito_item_cantidad CHECK (cantidad > 0)
);

COMMENT ON TABLE carrito_item IS 'Tabla puente N:M entre carrito y producto_talla';

CREATE INDEX idx_carrito_item_carrito ON carrito_item (id_carrito);



-- ---------------- Formulario de contacto ----------------
CREATE TABLE asunto_contacto (
    id_asunto  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre     VARCHAR(30) NOT NULL,
    activo     BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_asunto_nombre UNIQUE (nombre),
    CONSTRAINT chk_asunto_nombre CHECK (LENGTH(TRIM(nombre)) >= 3)
);

COMMENT ON TABLE asunto_contacto IS 'Consulta, Reclamo y Sugerencia: las 3 opciones del select de contacto.html';


CREATE TABLE mensaje_contacto (
    id_mensaje       INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_asunto        INT NOT NULL,
    id_ciudad        INT NOT NULL,
    id_cliente       INT,
    nombre           VARCHAR(60)  NOT NULL,
    email            VARCHAR(120) NOT NULL,
    descripcion      TEXT         NOT NULL,
    url_foto         VARCHAR(255),
    leido            BOOLEAN      NOT NULL DEFAULT FALSE,
    fecha_envio      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    respondido_por   INT,
    fecha_respuesta  TIMESTAMP,

    CONSTRAINT fk_mensaje_asunto
        FOREIGN KEY (id_asunto) REFERENCES asunto_contacto (id_asunto)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_mensaje_ciudad
        FOREIGN KEY (id_ciudad) REFERENCES ciudad (id_ciudad)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_mensaje_cliente
        FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT fk_mensaje_administrador
        FOREIGN KEY (respondido_por) REFERENCES administrador (id_administrador)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT chk_mensaje_nombre CHECK (LENGTH(TRIM(nombre)) >= 3),

    CONSTRAINT chk_mensaje_email CHECK (
        email ~* '^[^\s@]+@[^\s@]+\.[^\s@]{2,}$'
    ),

    CONSTRAINT chk_mensaje_descripcion CHECK (LENGTH(TRIM(descripcion)) >= 10),

    CONSTRAINT chk_mensaje_respuesta CHECK (
        fecha_respuesta IS NULL OR fecha_respuesta >= fecha_envio
    ),

    CONSTRAINT chk_mensaje_responsable CHECK (
        (fecha_respuesta IS NULL AND respondido_por IS NULL)
        OR (fecha_respuesta IS NOT NULL AND respondido_por IS NOT NULL)
    )
);

COMMENT ON TABLE mensaje_contacto IS 'Formulario de contacto. Replica todas las validaciones de validaciones.js';

CREATE INDEX idx_mensaje_asunto ON mensaje_contacto (id_asunto);
CREATE INDEX idx_mensaje_leido  ON mensaje_contacto (leido) WHERE leido = FALSE;



-- ---------------- Registro de cambios ----------------
CREATE TABLE auditoria (
    id_auditoria      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tabla_afectada    VARCHAR(50) NOT NULL,
    operacion         VARCHAR(10) NOT NULL,
    id_registro       INT,

    usuario_bd        VARCHAR(60) NOT NULL DEFAULT CURRENT_USER,

    datos_anteriores  JSONB,
    datos_nuevos      JSONB,
    fecha             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_auditoria_operacion CHECK (
        operacion IN ('INSERT', 'UPDATE', 'DELETE')
    ),

    CONSTRAINT chk_auditoria_datos CHECK (
        datos_anteriores IS NOT NULL OR datos_nuevos IS NOT NULL
    )
);

COMMENT ON TABLE auditoria IS 'Bitacora de cambios criticos. Guarda el estado anterior y nuevo en JSONB';

CREATE INDEX idx_auditoria_tabla ON auditoria (tabla_afectada, fecha);



-- ---------------- Cola de correos por enviar ----------------
-- El trigger deja aqui los recibos y Flask los envia despues
CREATE TABLE envio_correo (
    id_envio       INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pedido      INT NOT NULL,
    destinatario   VARCHAR(120) NOT NULL,
    asunto         VARCHAR(150) NOT NULL,
    estado         VARCHAR(15)  NOT NULL DEFAULT 'pendiente',
    intentos       SMALLINT     NOT NULL DEFAULT 0,
    error_detalle  TEXT,
    fecha_creado   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_enviado  TIMESTAMP,

    CONSTRAINT fk_envio_pedido
        FOREIGN KEY (id_pedido) REFERENCES pedido (id_pedido)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_envio_destinatario CHECK (
        destinatario ~* '^[^\s@]+@[^\s@]+\.[^\s@]{2,}$'
    ),

    CONSTRAINT chk_envio_estado CHECK (
        estado IN ('pendiente', 'enviado', 'fallido')
    ),

    CONSTRAINT chk_envio_intentos CHECK (intentos >= 0 AND intentos <= 5),

    CONSTRAINT chk_envio_fecha CHECK (
        fecha_enviado IS NULL OR fecha_enviado >= fecha_creado
    ),

    CONSTRAINT chk_envio_coherencia CHECK (
        (estado = 'enviado' AND fecha_enviado IS NOT NULL)
        OR (estado <> 'enviado')
    )
);

COMMENT ON TABLE envio_correo IS 'Cola de recibos en PDF. La llena un trigger y la vacia Flask por SMTP';

CREATE INDEX idx_envio_estado ON envio_correo (estado) WHERE estado = 'pendiente';
CREATE INDEX idx_envio_pedido ON envio_correo (id_pedido);
