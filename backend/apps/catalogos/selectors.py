from apps.catalogos.models import Categoria, Marca, ModeloActivo, Sede, Ubicacion


def listar_sedes(*, is_active=None, search=None):
    qs = Sede.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(nombre__icontains=search)
    return qs


def listar_ubicaciones(*, sede=None, is_active=None, search=None):
    qs = Ubicacion.objects.select_related("sede")
    if sede is not None:
        qs = qs.filter(sede=sede)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(nombre__icontains=search)
    return qs


def listar_categorias(*, is_active=None, search=None):
    qs = Categoria.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(nombre__icontains=search)
    return qs


def listar_marcas(*, is_active=None, search=None):
    qs = Marca.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(nombre__icontains=search)
    return qs


def listar_modelos(*, marca=None, categoria=None, is_active=None, search=None):
    qs = ModeloActivo.objects.select_related("marca", "categoria")
    if marca is not None:
        qs = qs.filter(marca=marca)
    if categoria is not None:
        qs = qs.filter(categoria=categoria)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(nombre__icontains=search)
    return qs
