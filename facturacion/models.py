# =====================================================================
# facturacion/models.py
# Cada CLASE es una TABLA. Cada ATRIBUTO es una COLUMNA. Cada OBJETO es una FILA.
# Django agrega solo la columna "id" (llave primaria) a cada tabla.
# Nombre de la tabla en la base de datos: <app>_<modelo>  →  facturacion_marca
# =====================================================================
from django.contrib.auth.models import User      # User: la tabla de usuarios que YA trae Django (auth_user)
from django.db import models                     # models: la clase Model y todos los tipos de campo


# ---------------------------------------------------------------------
# CATEGORÍA · tabla facturacion_categoria
# No tiene relaciones escritas aquí: la relación N:M con Producto se escribe en Producto.
# ---------------------------------------------------------------------
class Categoria(models.Model):                   # Hereda de models.Model → Django la convierte en tabla
    nombre = models.CharField(                   # CharField = texto corto → columna VARCHAR
        max_length=60,                           #   máximo 60 letras (OBLIGATORIO en CharField)
        unique=True,                             #   no puede haber dos categorías con el mismo nombre
    )
    descripcion = models.TextField(blank=True)   # TextField = texto largo. blank=True: el formulario lo deja vacío
    activo = models.BooleanField(default=True)   # Verdadero/Falso. default: valor si no se indica otro

    class Meta:                                  # Meta = configuración de la TABLA (no son columnas)
        verbose_name = "Categoría"               #   nombre en singular (se ve en el admin y en errores)
        verbose_name_plural = "Categorías"       #   nombre en plural
        ordering = ["nombre"]                    #   orden por defecto de las consultas: A → Z

    def __str__(self):                           # __str__ = cómo se muestra el objeto como TEXTO
        return self.nombre                       #   en listas y en el admin: "Laptops" y no "Categoria object (1)"


# ---------------------------------------------------------------------
# MARCA · tabla facturacion_marca
# Es el lado del "1" en la relación 1:N con Producto.
# ---------------------------------------------------------------------
class Marca(models.Model):
    nombre = models.CharField(max_length=60, unique=True)   # Nombre único: no se repite
    pais_origen = models.CharField(
        "País de origen",                        # 1er dato sin nombre = etiqueta bonita (verbose_name) para formularios
        max_length=60,
        blank=True,                              # opcional en el formulario
    )
    activo = models.BooleanField(default=True)   # Para "desactivar" en vez de borrar

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre                       # Ej: "Samsung"


# ---------------------------------------------------------------------
# PRODUCTO · tabla facturacion_producto
# Tiene DOS relaciones: 1:N con Marca y N:M con Categoria.
# ---------------------------------------------------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField("Descripción", blank=True)
    precio = models.DecimalField(                # DecimalField = número EXACTO con decimales (para dinero)
        max_digits=10,                           #   10 dígitos en total...
        decimal_places=2,                        #   ...de los cuales 2 son decimales → hasta 99 999 999.99
    )
    stock = models.PositiveIntegerField(default=0)   # Entero que no puede ser negativo

    # ---------- RELACIÓN UNO A MUCHOS (1:N) con Marca ----------
    # Pregunta: ¿un producto tiene varias marcas? NO.  ¿Una marca tiene varios productos? SÍ.  → 1:N
    # La ForeignKey se escribe en el lado de los "muchos" (Producto).
    # En la tabla crea la columna marca_id, que guarda el id de la marca. Ese número SÍ se puede repetir.
    marca = models.ForeignKey(
        Marca,                                   # ¿A qué modelo apunta? A Marca
        on_delete=models.PROTECT,                # ¿Qué pasa si borran la marca? PROTECT: no lo permite si tiene productos
        related_name="productos",                # Nombre del camino de vuelta: marca.productos.all()
    )

    # ---------- RELACIÓN MUCHOS A MUCHOS (N:M) con Categoría ----------
    # Pregunta: ¿un producto está en varias categorías? SÍ.  ¿Una categoría tiene varios productos? SÍ.  → N:M
    # NO crea una columna en esta tabla: una sola celda no puede guardar varios ids.
    # Django crea una TABLA INTERMEDIA (facturacion_producto_categorias) con dos columnas:
    # producto_id y categoria_id. Cada fila es un par "este producto está en esta categoría".
    categorias = models.ManyToManyField(
        Categoria,                               # ¿Con qué modelo? Con Categoria
        related_name="productos",                # Camino de vuelta: categoria.productos.all()
        blank=True,                              # Se puede guardar un producto sin categorías
    )                                            # Sin on_delete: si borras una categoría, solo se borran sus pares

    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)   # auto_now_add: guarda la fecha y hora al CREAR (sola)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.marca})"   # Usa el __str__ de Marca: "Galaxy A55 (Samsung)"


# ---------------------------------------------------------------------
# CLIENTE · tabla facturacion_cliente
# Sin relaciones por ahora. Más adelante una Venta tendrá una ForeignKey a Cliente.
# ---------------------------------------------------------------------
class Cliente(models.Model):
    cedula = models.CharField("Cédula", max_length=10, unique=True)   # Texto (no número): puede empezar con 0
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    email = models.EmailField("Correo", blank=True)                    # EmailField revisa que tenga formato de correo
    telefono = models.CharField("Teléfono", max_length=15, blank=True)
    direccion = models.CharField("Dirección", max_length=200, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["apellidos", "nombres"]      # Primero por apellido; si se repite, por nombre

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"   # Ej: "Pérez Ana"


# ---------------------------------------------------------------------
# PERFIL · tabla facturacion_perfil
# User de Django solo guarda usuario, contraseña, nombre y correo.
# Perfil guarda los datos EXTRA de cada usuario de Mi Tienda.
# ---------------------------------------------------------------------
class Perfil(models.Model):
    # ---------- RELACIÓN UNO A UNO (1:1) con User ----------
    # Pregunta: ¿un usuario tiene varios perfiles? NO.  ¿Un perfil es de varios usuarios? NO.  → 1:1
    # Es como una ForeignKey que NO se puede repetir: crea la columna usuario_id con valor ÚNICO.
    usuario = models.OneToOneField(
        User,                                    # ¿Con qué modelo? Con el User de Django
        on_delete=models.CASCADE,                # Si se borra el usuario, se borra su perfil (en cascada)
        related_name="perfil",                   # Camino de vuelta: request.user.perfil
    )
    cedula = models.CharField("Cédula", max_length=10, blank=True)
    telefono = models.CharField("Teléfono", max_length=15, blank=True)
    direccion = models.CharField("Dirección", max_length=200, blank=True)
    cargo = models.CharField(max_length=50, blank=True)   # Ej: Vendedor, Cajero, Administrador

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"   # Ej: "Perfil de maria"