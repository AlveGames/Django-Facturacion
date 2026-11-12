from django.contrib import messages                        # Mensajes
from django.contrib.auth import login, logout              # Abrir y cerrar sesión
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm   # NUEVO: UserCreationForm (registro)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def saludo(request):
    return HttpResponse("<h1>¡Hola desde Django!</h1><p>Esto es un HttpResponse.</p>")


def info_peticion(request):
    datos = {
        "metodo": request.method,
        "ruta": request.path,
        "parametros_get": request.GET.dict(),
        "navegador": request.headers.get("User-Agent", ""),
        # NUEVO: request.user dice quién está conectado. Si nadie, decimos "anónimo"
        "usuario": request.user.username if request.user.is_authenticated else "anónimo",
    }
    return JsonResponse(datos)


def home(request):
    nombre = ""
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
    contexto = {
        "titulo": "Mi Tienda",
        "nombre": nombre,
        "productos": ["Laptop", "Mouse", "Teclado"],
    }
    return render(request, "home.html", contexto)


# =====================================================================
# AUTENTICACIÓN · todo con funciones (VBF)
# =====================================================================

def ingresar(request):                                     # LOGIN
    if request.user.is_authenticated:
        return redirect("home")
    siguiente = request.POST.get("next") or request.GET.get("next") or ""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            messages.success(request, f"Hola, {usuario.username}.")
            if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
                return redirect(siguiente)
            return redirect("home")
    else:
        form = AuthenticationForm(request)
    return render(request, "registration/login.html", {"form": form, "next": siguiente})


@require_POST
def salir(request):                                        # LOGOUT (solo POST)
    logout(request)
    messages.info(request, "Cerraste sesión.")
    return redirect("login")


def registro(request):                                     # NUEVO: crear cuenta
    if request.user.is_authenticated:                      # Si ya inició sesión, no tiene sentido registrarse...
        return redirect("home")                            # ...lo enviamos al inicio

    if request.method == "POST":                           # ¿Presionó "Crear cuenta"?
        form = UserCreationForm(request.POST)              # Llenamos el formulario con lo que escribió
        if form.is_valid():                                # ¿Usuario libre y contraseñas iguales y seguras?
            usuario = form.save()                          # Crea el usuario con la contraseña CIFRADA
            login(request, usuario)                        # Abre su sesión de una vez
            messages.success(request, f"¡Bienvenido, {usuario.username}! Tu cuenta fue creada.")
            return redirect("home")
    else:                                                  # Llegó por GET...
        form = UserCreationForm()                          # ...formulario vacío

    return render(request, "registration/registro.html", {"form": form})