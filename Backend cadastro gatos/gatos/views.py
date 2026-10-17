from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import re

from .models import Pet, Interessado, Interesse, Visita

@require_GET
def listar_gatos(request):
    gatos = Pet.objects.filter(status='disponivel').values(
        'id', 'nome', 'idade', 'sexo', 'cor', 'descricao', 'foto',
    )
    return JsonResponse(list(gatos), safe=False)

@csrf_exempt
@require_POST
def registrar_intencao(request):
    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {'erro': 'O corpo da requisição deve conter um JSON válido.'},
            status=400,
        )

    nome = str(dados.get('nome') or '').strip()
    telefone = str(dados.get('telefone') or '').strip()
    tem_whatsapp = dados.get('tem_whatsapp', False)
    email = str(dados.get('email') or '').strip()
    pet_id = dados.get('pet_id')
    rotina = str(dados.get('rotina') or '').strip()

    if not nome or not telefone or not rotina or not pet_id:
        return JsonResponse(
            {'erro': 'Informe nome, telefone, gato e rotina.'},
            status=400,
        )

    if len(nome) > 100 or len(telefone) > 20 or len(email) > 100:
        return JsonResponse(
            {'erro': 'Um ou mais campos ultrapassam o tamanho permitido.'},
            status=400,
        )

    try:
        pet = Pet.objects.get(id=pet_id, status='disponivel')
    except (Pet.DoesNotExist, ValueError, TypeError):
        return JsonResponse(
            {'erro': 'O gato selecionado não existe ou não está disponível.'},
            status=400,
        )

    try:
        with transaction.atomic():
            interessado = Interessado.objects.create(
                nome=nome,
                telefone=telefone,
                tem_whatsapp=tem_whatsapp,
                email=email or None,
            )

            interesse = Interesse.objects.create(
                interessado=interessado,
                pet=pet,
                data_interesse=timezone.now(),
                status='pendente',
                mensagem=f'Rotina, lar e cuidados informados:\n{rotina}',
            )

    except Exception:
        return JsonResponse(
            {'erro': 'Não foi possível registrar a intenção de adoção.'},
            status=500,
        )

    return JsonResponse(
        {
            'mensagem': 'Intenção de adoção registrada com sucesso.',
            'interesse_id': interesse.id,
            'pet': pet.nome,
        },
        status=201,
    )

@require_GET
def localizar_intencoes_por_telefone(request):
    telefone = request.GET.get('telefone', '')
    telefone_digitado = re.sub(r'\D', '', telefone)

    if len(telefone_digitado) not in (10, 11):
        return JsonResponse(
            {'erro': 'Informe um telefone brasileiro válido com DDD.'},
            status=400,
        )

    # Compara apenas os números, ignorando parênteses,
    # espaços e hífens usados na formatação do telefone.
    interessados = [
        interessado
        for interessado in Interessado.objects.exclude(
            telefone__isnull=True
        ).only('id', 'telefone')
        if re.sub(r'\D', '', interessado.telefone or '') == telefone_digitado
    ]

    interesses = (
        Interesse.objects
        .filter(interessado__in=interessados)
        .select_related('pet')
        .order_by('-data_interesse')
    )

    resultados = [
        {
            'interesse_id': interesse.id,
            'pet': interesse.pet.nome,
        }
        for interesse in interesses
    ]

    return JsonResponse({'intencoes': resultados})

@csrf_exempt
@require_POST
def solicitar_visita(request):
    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {'erro': 'Envie um JSON válido.'},
            status=400,
        )

    interesse_id = dados.get('interesse_id')
    data_hora = dados.get('data_hora')
    observacoes = str(dados.get('observacoes') or '').strip()

    if not interesse_id or not data_hora:
        return JsonResponse(
            {'erro': 'Informe o interesse, a data e o horário desejados.'},
            status=400,
        )

    try:
        interesse = Interesse.objects.get(pk=interesse_id)
    except (Interesse.DoesNotExist, ValueError, TypeError):
        return JsonResponse(
            {'erro': 'Interesse não encontrado.'},
            status=404,
        )

    try:
        visita = Visita.objects.create(
            interesse=interesse,
            data_hora=data_hora,
            status='pendente',
            observacoes=observacoes or None,
        )
    except (ValueError, TypeError):
        return JsonResponse(
            {'erro': 'Data ou horário inválidos.'},
            status=400,
        )

    return JsonResponse(
        {
            'mensagem': 'Solicitação de visita registrada com sucesso.',
            'visita_id': visita.id,
            'status': visita.status,
        },
        status=201,
    )