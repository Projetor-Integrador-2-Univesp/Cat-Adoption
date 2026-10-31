"""Formulários públicos de intenção de adoção e solicitação de visita."""

import json
import os
import re
from datetime import datetime, timedelta

from django.conf import settings
from django.core import signing
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Adocao, Interessado, Interesse, Pet, Visita


TOKEN_SALT = "larbastet-solicitacao-visita"
TOKEN_VALIDADE = 30 * 24 * 60 * 60


def _chave_visita():
    chave = os.environ.get("VISITA_SIGNING_KEY")
    if chave:
        return chave
    if (settings.DEBUG and
            settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"):
        return settings.SECRET_KEY
    raise ImproperlyConfigured("Defina VISITA_SIGNING_KEY antes de publicar o formulário.")


def _ler_json(request):
    if request.content_type != "application/json":
        return None, JsonResponse({"erro": "Envie os dados em JSON."}, status=415)
    if len(request.body) > 8192:
        return None, JsonResponse({"erro": "Formulário muito grande."}, status=413)
    try:
        dados = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return None, JsonResponse({"erro": "JSON inválido."}, status=400)
    if not isinstance(dados, dict):
        return None, JsonResponse({"erro": "Envie um objeto JSON."}, status=400)
    return dados, None


@csrf_exempt
@require_POST
def registrar_intencao(request):
    dados, erro = _ler_json(request)
    if erro is not None:
        return erro

    chave_assinatura = _chave_visita()
    nome = str(dados.get("nome") or "").strip()
    telefone = str(dados.get("telefone") or "").strip()
    email = str(dados.get("email") or "").strip()
    rotina = str(dados.get("rotina") or "").strip()
    residencia = str(dados.get("tipo_residencia") or "").strip()
    pet_id = dados.get("pet_id")

    if not all((nome, telefone, rotina, residencia)):
        return JsonResponse({"erro": "Preencha os campos obrigatórios."}, status=400)
    if (len(nome) > 100 or len(telefone) > 20 or len(email) > 100
            or len(rotina) > 2000):
        return JsonResponse({"erro": "Um dos campos ultrapassa o limite permitido."}, status=400)
    if len(re.sub(r"\D", "", telefone)) not in (10, 11):
        return JsonResponse({"erro": "Informe um telefone com DDD."}, status=400)
    if residencia not in dict(Interessado.TIPO_RESIDENCIA_CHOICES):
        return JsonResponse({"erro": "Tipo de residência inválido."}, status=400)
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"erro": "E-mail inválido."}, status=400)
    try:
        pet_id = int(pet_id)
        if pet_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({"erro": "Selecione um gato válido."}, status=400)

    with transaction.atomic():
        pet = Pet.objects.filter(pk=pet_id, status="disponivel").first()
        if pet is None:
            return JsonResponse({"erro": "O gato não está disponível."}, status=409)
        interessado = Interessado.objects.create(
            nome=nome, telefone=telefone, email=email or None,
            tipo_residencia=residencia,
        )
        interesse = Interesse.objects.create(
            interessado=interessado, pet=pet, status="pendente",
            mensagem=f"Rotina e cuidados informados:\n{rotina}",
        )

    token = signing.dumps({"interesse": interesse.pk}, key=chave_assinatura, salt=TOKEN_SALT)
    return JsonResponse({
        "mensagem": "Intenção registrada com sucesso.",
        "interesse_id": interesse.pk,
        "pet": pet.nome or "Sem nome",
        "token_visita": token,
    }, status=201)


@csrf_exempt
@require_POST
def solicitar_visita(request):
    dados, erro = _ler_json(request)
    if erro is not None:
        return erro

    try:
        interesse_id = int(dados.get("interesse_id"))
        if interesse_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({"erro": "Intenção inválida."}, status=400)

    token = dados.get("token_visita")
    if not isinstance(token, str) or len(token) > 1000:
        return JsonResponse({"erro": "Comprovante da intenção inválido."}, status=403)
    try:
        comprovante = signing.loads(token, key=_chave_visita(), salt=TOKEN_SALT, max_age=TOKEN_VALIDADE)
    except signing.BadSignature:
        return JsonResponse({"erro": "Comprovante inválido ou expirado."}, status=403)
    if not isinstance(comprovante, dict) or comprovante.get("interesse") != interesse_id:
        return JsonResponse({"erro": "Comprovante não corresponde à intenção."}, status=403)

    observacoes = str(dados.get("observacoes") or "").strip()
    if len(observacoes) > 1000:
        return JsonResponse({"erro": "Observações muito longas."}, status=400)

    try:
        data_hora = datetime.fromisoformat(str(dados.get("data_hora") or "").replace("Z", "+00:00"))
        if timezone.is_naive(data_hora):
            raise ValueError
    except ValueError:
        return JsonResponse({"erro": "Informe uma data e horário válidos com fuso horário."}, status=400)

    agora = timezone.now()
    if not (agora < data_hora <= agora + timedelta(days=90)):
        return JsonResponse({"erro": "Escolha uma data futura dentro dos próximos 90 dias."}, status=400)

    with transaction.atomic():
        interesse = (Interesse.objects.select_for_update().select_related("pet")
                     .filter(pk=interesse_id).first())
        if interesse is None or interesse.status == "recusado" or interesse.pet.status == "adotado":
            return JsonResponse({"erro": "Esta intenção não permite agendar visitas."}, status=409)
        if Adocao.objects.filter(interesse=interesse).exists():
            return JsonResponse({"erro": "Esta intenção já resultou em uma adoção."}, status=409)
        if Visita.objects.filter(interesse=interesse, status__in=["pendente", "agendada"]).exists():
            return JsonResponse({"erro": "Já existe uma visita pendente ou agendada."}, status=409)
        visita = Visita.objects.create(
            interesse=interesse, data_hora=data_hora,
            observacoes=observacoes or None, status="pendente",
        )

    return JsonResponse({
        "mensagem": "Solicitação registrada. Aguarde a confirmação da responsável.",
        "visita_id": visita.pk,
    }, status=201)
