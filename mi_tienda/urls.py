from django.contrib import admin
from django.urls import path, include
from . import views                                    # Nuestras vistas (también ingresar y salir)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("saludo/", views.saludo, name="saludo"),
    path("info/", views.info_peticion, name="info"),

    # ---------- AUTENTICACIÓN (funciones) ----------
    # name="login" es importante: LOGIN_URL de settings.py lo usa para saber a dónde enviar
    path("login/", views.ingresar, name="login"),      # GET: formulario · POST: revisa y abre la sesión
    path("logout/", views.salir, name="logout"),       # Solo POST: cierra la sesión

    path("facturacion/", include("facturacion.urls")),
    path("registro/", views.registro, name="registro"),   # GET: formulario · POST: crea el usuario
]