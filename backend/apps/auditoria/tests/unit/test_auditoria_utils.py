from apps.auditoria.utils import get_client_ip, sanitizar_entidad_id


def test_sanitizar_entidad_id_valido():
    assert sanitizar_entidad_id("ana@x.com") == "ana@x.com"


def test_sanitizar_entidad_id_mas_64_con_arroba():
    largo = ("a" * 60) + "@x.com"
    assert len(largo) > 64
    assert sanitizar_entidad_id(largo) == ""


def test_sanitizar_entidad_id_sin_arroba():
    assert sanitizar_entidad_id("usuario123") == ""
    assert sanitizar_entidad_id("") == ""
    assert sanitizar_entidad_id(None) == ""


def test_get_client_ip_default_remote_addr(settings, rf):
    settings.TRUST_X_FORWARDED_FOR = False
    request = rf.get("/", REMOTE_ADDR="10.0.0.5", HTTP_X_FORWARDED_FOR="1.2.3.4, 5.6.7.8")
    assert get_client_ip(request) == "10.0.0.5"


def test_get_client_ip_trust_x_forwarded_for(settings, rf):
    settings.TRUST_X_FORWARDED_FOR = True
    request = rf.get("/", REMOTE_ADDR="10.0.0.5", HTTP_X_FORWARDED_FOR="1.2.3.4, 5.6.7.8")
    assert get_client_ip(request) == "1.2.3.4"
