"""Atualização de status e registro de adoções no painel administrativo."""

from datetime import date

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import Adocao, Interesse, Pet, Visita


def _staff_only(request):
    if not request.user.is_staff:
        return JsonResponse({"erro": "Acesso restrito à administração."}, status=403)
    return None


@login_required(login_url="login")
@require_POST
def atualizar_status_interesse(request, interesse_id):
    denied = _staff_only(request)
    if denied is not None:
        return denied

    novo_status = request.POST.get("status", "").strip()
    if novo_status not in dict(Interesse.STATUS_CHOICES):
        return JsonResponse({"erro": "Status da intenção inválido."}, status=400)

    with transaction.atomic():
        # Mantém a mesma ordem de bloqueio usada no registro de adoções.
        interesse_base = get_object_or_404(Interesse, pk=interesse_id)
        pet = Pet.objects.select_for_update().get(pk=interesse_base.pet_id)
        interesse = Interesse.objects.select_for_update().get(pk=interesse_id)
        # A intenção de uma adoção concluída deve permanecer aprovada.
        if Adocao.objects.filter(interesse_id=interesse.pk).exists() and novo_status != "aprovado":
            return JsonResponse({"erro": "Não é possível retirar a aprovação de uma adoção registrada."}, status=409)
        if novo_status == "aprovado" and pet.status == "adotado":
            if not Adocao.objects.filter(interesse_id=interesse.pk).exists():
                return JsonResponse({"erro": "Este gato já consta como adotado."}, status=409)
        interesse.status = novo_status
        interesse.save(update_fields=["status"])

    return JsonResponse({"id": interesse.pk, "status": interesse.get_status_display(), "status_codigo": interesse.status})


@login_required(login_url="login")
@require_POST
def atualizar_status_visita(request, visita_id):
    denied = _staff_only(request)
    if denied is not None:
        return denied

    novo_status = request.POST.get("status", "").strip()
    if novo_status not in dict(Visita.STATUS_CHOICES):
        return JsonResponse({"erro": "Status da visita inválido."}, status=400)

    with transaction.atomic():
        visita = get_object_or_404(Visita.objects.select_for_update(), pk=visita_id)
        visita.status = novo_status
        visita.save(update_fields=["status"])

    return JsonResponse({"id": visita.pk, "status": visita.get_status_display(), "status_codigo": visita.status})


@login_required(login_url="login")
@require_POST
def registrar_adocao(request):
    denied = _staff_only(request)
    if denied is not None:
        return denied

    try:
        interesse_id = int(request.POST.get("interesse_id", ""))
        if interesse_id <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"erro": "Selecione uma intenção válida."}, status=400)

    observacoes = request.POST.get("observacoes", "").strip()
    if len(observacoes) > 2000:
        return JsonResponse({"erro": "Observações muito longas (máximo 2.000 caracteres)."}, status=400)

    data_texto = request.POST.get("data_adocao", "").strip()
    try:
        data_adocao = date.fromisoformat(data_texto) if data_texto else date.today()
    except ValueError:
        return JsonResponse({"erro": "Data de adoção inválida (use AAAA-MM-DD)."}, status=400)
    if data_adocao > date.today():
        return JsonResponse({"erro": "A data de adoção não pode estar no futuro."}, status=400)

    with transaction.atomic():
        interesse = get_object_or_404(Interesse.objects.select_related("pet"), pk=interesse_id)
        # O bloqueio reduz o risco de adoções simultâneas do mesmo gato.
        pet = Pet.objects.select_for_update().get(pk=interesse.pet_id)
        interesse = Interesse.objects.select_for_update().get(pk=interesse_id)
        if Adocao.objects.filter(interesse__pet_id=pet.pk).exists():
            return JsonResponse({"erro": "Este gato já possui uma adoção registrada."}, status=409)
        if pet.status == "adotado":
            return JsonResponse({"erro": "Este gato já está marcado como adotado."}, status=409)
        if interesse.status != "aprovado":
            return JsonResponse({"erro": "A intenção precisa estar aprovada antes da adoção."}, status=409)
        adocao = Adocao.objects.create(
            interesse=interesse, data_adocao=data_adocao, observacoes=observacoes
        )
        pet.status = "adotado"
        pet.save(update_fields=["status"])

    return JsonResponse({"id": adocao.pk, "mensagem": "Adoção registrada com sucesso."}, status=201)
