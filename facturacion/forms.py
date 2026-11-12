from django import forms                                 # Herramientas de formularios
from .models import Categoria, Cliente, Marca, Producto, Perfil            # Categoria: para la tarea (Unidad 5)                   # NUEVO: también importamos Producto


class MarcaForm(forms.ModelForm):                        # (Sin cambios, de la Unidad 2)
    class Meta:
        model = Marca
        fields = ["nombre", "pais_origen", "activo"]
        labels = {"nombre": "Nombre de la marca"}
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Samsung"}),
            "pais_origen": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Corea del Sur"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 letras.")
        return nombre.title()


class ProductoForm(forms.ModelForm):                     # NUEVO: formulario de Producto
    class Meta:
        model = Producto                                 # Sale del modelo Producto
        fields = ["nombre", "descripcion", "marca", "categorias", "precio", "stock", "activo"]  # Campos en orden
        widgets = {                                      # Cómo se dibuja cada campo en HTML
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Laptop Pro 14"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),   # Caja grande de 3 líneas
            # 1:N (ForeignKey) → lista desplegable <select>: se elige UNA sola marca
            "marca": forms.Select(attrs={"class": "form-select"}),
            # N:M (ManyToMany) → una casilla por categoría: se pueden marcar VARIAS
            "categorias": forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),  # Con centavos
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),    # Entero, mínimo 0
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):                 # __init__ se ejecuta al crear el formulario: ProductoForm(...)
        super().__init__(*args, **kwargs)                # Primero dejamos que Django arme el formulario normal
        # Luego cambiamos las opciones de la lista de marcas: solo las activas
        self.fields["marca"].queryset = Marca.objects.filter(activo=True)
        self.fields["marca"].empty_label = "— Elige una marca —"   # Texto de la primera opción de la lista

    def clean_precio(self):                              # Validación propia del campo precio
        precio = self.cleaned_data["precio"]             # El precio ya convertido a número por Django
        if precio <= 0:                                  # Si es 0 o negativo...
            raise forms.ValidationError("El precio debe ser mayor que 0.")   # ...error en rojo bajo el campo
        return precio                                    # Si está bien, lo devolvemos


# =====================================================================
# TAREA 1 · CATEGORÍAS (Unidad 5)
# =====================================================================
class CategoriaForm(forms.ModelForm):                    # Formulario construido desde el modelo Categoria
    class Meta:
        model = Categoria                                # ¿De qué modelo sale? De Categoria
        fields = ["nombre", "descripcion", "activo"]     # Campos que muestra y en qué orden
        labels = {"nombre": "Nombre de la categoría"}    # Texto de la etiqueta del campo nombre
        widgets = {                                      # Cómo se dibuja cada campo en HTML
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Laptops"}),
            # Textarea = caja grande de varias líneas (igual que la descripción de Producto)
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):                              # Validación propia del campo nombre
        nombre = self.cleaned_data["nombre"].strip()     # Quitamos los espacios de los lados
        if len(nombre) < 3:                              # Mínimo 3 letras...
            raise forms.ValidationError("El nombre debe tener al menos 3 letras.")   # ...si no, error en rojo
        return nombre[0].upper() + nombre[1:]            # Solo la PRIMERA letra en mayúscula: "  ofertas " → "Ofertas"

    

# =====================================================================
# TAREA 2 · CLIENTES (Unidad 5)
# =====================================================================
class ClienteForm(forms.ModelForm):                      # Formulario construido desde el modelo Cliente
    class Meta:
        model = Cliente
        # Todos los campos MENOS fecha_registro: esa se llena sola (auto_now_add=True)
        fields = ["cedula", "nombres", "apellidos", "email", "telefono", "direccion"]
        widgets = {                                      # Cómo se dibuja cada campo en HTML
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 0912345678"}),
            "nombres": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Ana María"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Pérez López"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Ej: ana@correo.com"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 0991234567"}),
            "direccion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Av. 9 de Octubre"}),
        }

    def clean_cedula(self):                              # Validación propia (base: clean_precio)
        cedula = self.cleaned_data["cedula"].strip()     # Quitamos espacios de los lados
        if len(cedula) != 10:                            # 1. Exactamente 10 caracteres
            raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos.")
        if not cedula.isdigit():                         # 2. isdigit(): True solo si TODOS son números
            raise forms.ValidationError("La cédula debe tener solo números.")
        return cedula                                    # Que no se repita lo revisa unique=True del modelo



# =====================================================================
# RETO · MI PERFIL (relación 1:1 con User)
# =====================================================================
class PerfilForm(forms.ModelForm):                       # Formulario construido desde el modelo Perfil
    class Meta:
        model = Perfil
        # SIN "usuario": ese no lo elige nadie, siempre es request.user (lo pone la vista)
        fields = ["cedula", "telefono", "direccion", "cargo"]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 0912345678"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 0991234567"}),
            "direccion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Av. 9 de Octubre"}),
            "cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Vendedor"}),
        }