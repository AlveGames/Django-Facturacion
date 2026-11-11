from django.contrib import admin                                # El panel de administración
from .models import Categoria, Marca, Producto, Cliente, Perfil # Nuestros modelos (el punto = de esta app)

# Forma simple: el modelo aparece en el panel
admin.site.register(Categoria)                          # Registra Categoría
admin.site.register(Marca)                              # Registra Marca
admin.site.register(Cliente)                            # Registra Cliente
admin.site.register(Perfil)                             # Registra Perfil (relación 1:1 con User)


# Forma con opciones: decides qué columnas ver, por qué buscar y por qué filtrar
@admin.register(Producto)                               # Registra Producto con la configuración de abajo
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "marca", "precio", "stock", "activo")   # Columnas. Una ManyToMany NO se puede poner aquí
    search_fields = ("nombre",)                         # Caja de búsqueda por nombre (la coma final es necesaria)
    list_filter = ("marca", "categorias", "activo")     # Filtros en el lado derecho (aquí sí sirve la N:M)
    filter_horizontal = ("categorias",)                 # Dos cajas para pasar categorías de un lado a otro (N:M)