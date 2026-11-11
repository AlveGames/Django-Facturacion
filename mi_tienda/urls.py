from django.contrib import admin
from django.urls import path, include      # ← NUEVO: include sirve para sumar las URLs de una app
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("saludo/", views.saludo, name="saludo"),
    path("info/", views.info_peticion, name="info"),
    # Todo lo que empiece con "facturacion/" lo atiende facturacion/urls.py
    path("facturacion/", include("facturacion.urls")),
]