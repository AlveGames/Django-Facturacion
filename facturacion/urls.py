from django.urls import path               # path() une una dirección con una vista
from . import views                        # Las vistas de ESTA app (facturacion/views.py)

app_name = "facturacion"                   # "Apellido" de las URLs de esta app. En templates: 'facturacion:marca_lista'

urlpatterns = [
    path("marcas/", views.marca_lista, name="marca_lista"),   # /facturacion/marcas/ → vista marca_lista
    path("marcas/crear/", views.marca_crear, name="marca_crear"),   # /facturacion/marcas/crear/
        # <int:pk> captura el número de la URL y se lo pasa a la vista como parámetro pk
    path("marcas/editar/<int:pk>/", views.marca_editar, name="marca_editar"),
    path("marcas/eliminar/<int:pk>/", views.marca_eliminar, name="marca_eliminar"),
        # ---------- PRODUCTOS (Unidad 3) ----------
    path("productos/", views.producto_lista, name="producto_lista"),   # /facturacion/productos/
    path("productos/crear/", views.producto_crear, name="producto_crear"),   # /facturacion/productos/crear/
        # <int:pk> captura el número de la URL y se lo pasa a la función como parámetro pk
    path("productos/editar/<int:pk>/", views.producto_editar, name="producto_editar"),
    path("productos/<int:pk>/", views.producto_detalle, name="producto_detalle"),   # /facturacion/productos/7/
]