from django.contrib import messages                        # Mensajes de éxito y error
from django.core.paginator import Paginator                # NUEVO: corta una lista en páginas
from django.db.models import ProtectedError                # Error al borrar una marca que tiene productos
from django.shortcuts import render, redirect, get_object_or_404

from .forms import MarcaForm, ProductoForm                 # NUEVO: ProductoForm
from .models import Marca, Producto                        # NUEVO: Producto

from django.contrib.auth.decorators import login_required


# =====================================================================
# MARCAS · Vistas Basadas en Funciones (VBF)
# =====================================================================
@login_required
def marca_lista(request):                                  # READ: muestra todas las marcas
    q = request.GET.get("q", "")                           # 1. Leemos el buscador: /facturacion/marcas/?q=sam (si no hay, queda "")
    marcas = Marca.objects.all()                           # 2. Pedimos todas las marcas a la base de datos

    if q:                                                  # 3. Si el usuario escribió algo en el buscador...
        marcas = marcas.filter(nombre__icontains=q)        #    ...dejamos solo las que contienen ese texto

    contexto = {                                           # 4. Datos que enviamos al template
        "titulo": "Marcas",                                #    → {{ titulo }}
        "marcas": marcas,                                  #    → {% for marca in marcas %}
        "q": q,                                            #    → para que el buscador no se borre
    }
    return render(request, "facturacion/marca_lista.html", contexto)   # 5. Mostramos la página




@login_required
def marca_crear(request):                                  # CREATE: crear una marca nueva

    if request.method == "POST":                           # ¿El usuario presionó "Guardar"? (llegó por POST)
        form = MarcaForm(request.POST)                     # 1. Llenamos el formulario con lo que escribió
        if form.is_valid():                                # 2. ¿Los datos están bien? (obligatorios, únicos, clean_nombre)
            marca = form.save()                            # 3. Guardamos en la base de datos (save devuelve la marca)
            messages.success(request, f"Marca «{marca.nombre}» creada correctamente.")   # 4. Mensaje verde
            return redirect("facturacion:marca_lista")     # 5. Vamos a la lista. Así, si recarga, no se guarda dos veces
        # Si NO es válido, no entra al if: baja hasta el render y muestra el formulario CON errores

    else:                                                  # Si llegó por GET (solo abrió la página)...
        form = MarcaForm()                                 # ...creamos un formulario vacío

    contexto = {                                           # Datos para el template
        "titulo": "Nueva marca",                           # Título de la página
        "form": form,                                      # El formulario (vacío o con errores)
        "boton": "Guardar",                                # Texto del botón
    }
    return render(request, "facturacion/marca_form.html", contexto)



@login_required
def marca_editar(request, pk):                             # UPDATE. pk llega desde la URL: /marcas/editar/3/ → pk=3
    marca = get_object_or_404(Marca, pk=pk)                # 1. Buscamos la marca. Si no existe → página 404

    if request.method == "POST":                           # 2. ¿Presionó "Actualizar"?
        form = MarcaForm(request.POST, instance=marca)     #    Datos nuevos + la marca que vamos a cambiar
        if form.is_valid():                                #    ¿Están bien?
            form.save()                                    #    Actualiza (UPDATE), no crea una nueva
            messages.success(request, f"Marca «{marca.nombre}» actualizada.")
            return redirect("facturacion:marca_lista")     #    Volvemos a la lista
    else:                                                  # 3. Llegó por GET...
        form = MarcaForm(instance=marca)                   #    ...formulario lleno con los datos actuales

    contexto = {
        "titulo": f"Editar marca: {marca.nombre}",
        "form": form,
        "boton": "Actualizar",
    }
    return render(request, "facturacion/marca_form.html", contexto)   # ¡El mismo template de crear!


@login_required
def marca_eliminar(request, pk):                           # DELETE
    marca = get_object_or_404(Marca, pk=pk)                # Buscamos la marca o mostramos 404

    if request.method == "POST":                           # ¿Presionó "Sí, eliminar"?
        try:                                               # Intentamos borrar...
            nombre = marca.nombre                          # Guardamos el nombre para el mensaje
            marca.delete()                                 # DELETE en la base de datos
            messages.success(request, f"Marca «{nombre}» eliminada.")
        except ProtectedError:                             # ...si tiene productos, PROTECT no deja borrarla
            messages.error(request, f"No se puede eliminar «{marca.nombre}» porque tiene productos. Desactívala en su lugar.")
        return redirect("facturacion:marca_lista")         # En los dos casos volvemos a la lista

    # Si llegó por GET: mostramos la pregunta "¿Seguro?"
    contexto = {"titulo": "Eliminar marca", "marca": marca}
    return render(request, "facturacion/marca_eliminar.html", contexto)



# =====================================================================
# PRODUCTOS · Vistas Basadas en Funciones (VBF)
# =====================================================================
@login_required
def producto_lista(request):                               # READ: lista de productos con buscador y páginas
    q = request.GET.get("q", "")                           # 1. Texto del buscador: /productos/?q=laptop (si no hay, "")

    productos = (                                          # 2. Pedimos los productos a la base de datos
        Producto.objects
        .select_related("marca")                           #    1:N → trae la marca en la MISMA consulta (JOIN)
        .prefetch_related("categorias")                    #    N:M → trae todas las categorías en UNA consulta extra
    )                                                      #    Sin estas 2 líneas la tabla haría 2 consultas POR CADA producto

    if q:                                                  # 3. Si escribió algo en el buscador...
        productos = productos.filter(nombre__icontains=q)  #    ...dejamos solo los que contienen ese texto

    paginador = Paginator(productos, 5)                    # 4. Corta la lista de 5 en 5
    numero = request.GET.get("page")                       # 5. ¿Qué página pidió? /productos/?page=2 (si no hay, None)
    page_obj = paginador.get_page(numero)                  # 6. Esa página. Si piden ?page=abc da la 1; si piden ?page=99, la última

    contexto = {
        "titulo": "Productos",                             # → {{ titulo }}
        "page_obj": page_obj,                              # → {% for producto in page_obj %} (solo trae los 5 de esta página)
        "q": q,                                            # → para que el buscador no se borre
    }
    return render(request, "facturacion/producto_lista.html", contexto)

@login_required
def producto_crear(request):                               # CREATE: crear un producto nuevo

    if request.method == "POST":                           # ¿Presionó "Guardar"? (llegó por POST)
        form = ProductoForm(request.POST)                  # 1. Llenamos el formulario con lo que envió
        if form.is_valid():                                # 2. ¿Todo bien? (obligatorios, marca existe, clean_precio...)
            producto = form.save()                         # 3. INSERT del producto + INSERT de sus categorías (N:M)
            messages.success(request, f"Producto «{producto.nombre}» creado.")
            return redirect("facturacion:producto_lista")  # 4. A la lista (Post/Redirect/Get)
        # Si NO es válido, baja hasta el render y muestra el formulario CON errores

    else:                                                  # Llegó por GET (abrió la página)...
        form = ProductoForm()                              # ...formulario vacío

    contexto = {
        "titulo": "Nuevo producto",
        "form": form,                                      # Vacío (GET) o con datos y errores (POST inválido)
        "boton": "Guardar",
    }
    return render(request, "facturacion/producto_form.html", contexto)

@login_required
def producto_editar(request, pk):                          # UPDATE. pk viene de la URL: /productos/editar/7/ → pk=7
    producto = get_object_or_404(Producto, pk=pk)          # 1. Buscamos el producto. Si no existe → página 404

    if request.method == "POST":                           # 2. ¿Presionó "Actualizar"?
        form = ProductoForm(request.POST, instance=producto)   # Datos nuevos + el producto que vamos a cambiar
        if form.is_valid():
            form.save()                                    # UPDATE del producto y reemplaza sus categorías por las marcadas
            messages.success(request, f"Producto «{producto.nombre}» actualizado.")
            return redirect("facturacion:producto_lista")
        messages.error(request, "Revisa los campos marcados en rojo.")   # Solo llega aquí si NO es válido
    else:                                                  # 3. Llegó por GET...
        form = ProductoForm(instance=producto)             #    ...formulario LLENO con los datos actuales (y sus casillas marcadas)

    contexto = {
        "titulo": f"Editar producto: {producto.nombre}",
        "form": form,
        "boton": "Actualizar",
    }
    return render(request, "facturacion/producto_form.html", contexto)   # El mismo template de crear

@login_required
def producto_detalle(request, pk):                         # READ (uno): la ficha de un producto
    producto = get_object_or_404(Producto, pk=pk)          # Buscamos el producto número pk o mostramos 404
    contexto = {"producto": producto}                      # Solo necesitamos enviar el producto
    return render(request, "facturacion/producto_detalle.html", contexto)
    # Esta vista solo atiende GET: no tiene formulario, así que no pregunta por request.method

@login_required
def producto_eliminar(request, pk):                        # DELETE
    producto = get_object_or_404(Producto, pk=pk)          # Buscamos el producto o mostramos 404

    if request.method == "POST":                           # ¿Presionó "Sí, eliminar"?
        nombre = producto.nombre                           # Guardamos el nombre para el mensaje
        producto.delete()                                  # DELETE del producto y de sus filas en la tabla intermedia
        messages.success(request, f"Producto «{nombre}» eliminado.")   # (la marca y las categorías NO se borran)
        return redirect("facturacion:producto_lista")

    # Llegó por GET: mostramos la pregunta "¿Seguro?"
    contexto = {"titulo": "Eliminar producto", "producto": producto}
    return render(request, "facturacion/producto_eliminar.html", contexto)