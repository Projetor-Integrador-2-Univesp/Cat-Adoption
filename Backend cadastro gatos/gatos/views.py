from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json

from .models import Pet, Interessado, Interesse

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
