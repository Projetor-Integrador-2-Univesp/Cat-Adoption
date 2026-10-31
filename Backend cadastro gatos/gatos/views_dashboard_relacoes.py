"""Consultas de interessados, intenções, visitas e adoções para o painel."""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Adocao, Interessado, Interesse, Visita


def _staff_required(request):
    if not request.user.is_staff:
        return JsonResponse({"erro": "Acesso restrito à administração."}, status=403)
    return None


@login_required(login_url="login")
@require_GET
def listar_interessados(request):
    denied = _staff_required(request)
    if denied is not None:
        return denied
    pessoas = Interessado.objects.all().order_by("nome", "pk")
    data = [{
        "id": obj.pk,
        "nome": obj.nome,
        "cpf": obj.cpf or "",
        "email": obj.email or "",
        "telefone": obj.telefone or "",
        "endereco": obj.endereco or "",
        "tipo_residencia": obj.get_tipo_residencia_display(),
    } for obj in pessoas]
    return JsonResponse(data, safe=False)


@login_required(login_url="login")
@require_GET
def listar_interesses(request):
    denied = _staff_required(request)
    if denied is not None:
        return denied
    interesses = (Interesse.objects.select_related("interessado", "pet")
                 .order_by("-data_interesse", "-pk"))
    data = [{
        "id": obj.pk,
        "interessado": obj.interessado.nome,
        "telefone": obj.interessado.telefone or "",
        "email": obj.interessado.email or "",
        "pet": obj.pet.nome or "Sem nome",
        "mensagem": obj.mensagem or "",
        "status": obj.get_status_display(),
        "status_codigo": obj.status,
        "data_interesse": obj.data_interesse.isoformat() if obj.data_interesse else "",
    } for obj in interesses]
    return JsonResponse(data, safe=False)


@login_required(login_url="login")
@require_GET
def listar_visitas(request):
    denied = _staff_required(request)
    if denied is not None:
        return denied
    visitas = (Visita.objects.select_related("interesse__interessado", "interesse__pet")
               .order_by("-data_hora", "-pk"))
    data = [{
        "id": obj.pk,
        "interessado": obj.interesse.interessado.nome,
        "pet": obj.interesse.pet.nome or "Sem nome",
        "data_hora": obj.data_hora.isoformat() if obj.data_hora else "",
        "status": obj.get_status_display(),
        "status_codigo": obj.status,
        "observacoes": obj.observacoes or "",
    } for obj in visitas]
    return JsonResponse(data, safe=False)


@login_required(login_url="login")
@require_GET
def listar_adocoes(request):
    denied = _staff_required(request)
    if denied is not None:
        return denied
    adocoes = (Adocao.objects.select_related("interesse__interessado", "interesse__pet")
               .order_by("-data_adocao", "-pk"))
    data = []
    for obj in adocoes:
        interesse = obj.interesse
        data.append({
            "id": obj.pk,
            "interesse_id": interesse.pk if interesse else None,
            "interessado": interesse.interessado.nome if interesse else "Não vinculado",
            "pet": (interesse.pet.nome or "Sem nome") if interesse else "Não vinculado",
            "data_adocao": obj.data_adocao.isoformat() if obj.data_adocao else "",
            "observacoes": obj.observacoes or "",
        })
    return JsonResponse(data, safe=False)
