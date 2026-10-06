import json

import os
import uuid
from supabase import create_client

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Pet, Adotante, Adocao, SolicitacaoAdocao


def pet_to_dict(pet, request=None):
    return {
        "id": pet.id,
        "nome": pet.nome,
        "idade": pet.idade,
        "sexo": pet.sexo,
        "sexo_display": pet.get_sexo_display(),
        "cor": pet.cor,
        "descricao": pet.descricao,
        "status": pet.status,
        "status_display": pet.get_status_display(),
        "data_entrada": pet.data_entrada.strftime("%Y-%m-%d") if pet.data_entrada else None,
        "foto": pet.foto_url,
    }


def adotante_to_dict(adotante):
    return {
        "cpf": adotante.cpf,
        "nome": adotante.nome,
        "email": adotante.email,
        "telefone": adotante.telefone,
        "endereco": adotante.endereco,
    }


def adocao_to_dict(adocao):
    return {
        "id": adocao.id,
        "pet": {
            "id": adocao.pet.id,
            "nome": adocao.pet.nome,
        },
        "adotante": {
            "cpf": adocao.adotante.cpf,
            "nome": adocao.adotante.nome,
        },
        "data_adocao": adocao.data_adocao.strftime("%Y-%m-%d"),
        "observacoes": adocao.observacoes,
    }

def solicitacao_to_dict(solicitacao):
    return {
        "id": solicitacao.id,
        "nome": solicitacao.nome,
        "telefone": solicitacao.telefone,
        "email": solicitacao.email,
        "animal_interesse": solicitacao.animal_interesse,
        "mensagem": solicitacao.mensagem,
        "status": solicitacao.status,
        "status_display": solicitacao.get_status_display(),
        "data_envio": solicitacao.data_envio.strftime("%Y-%m-%d %H:%M:%S"),
    }


def json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


# Endpoint público usado pelo site
def listar_gatos(request):
    gatos = Pet.objects.filter(status='disponivel').order_by('-data_entrada')
    return JsonResponse(
        [pet_to_dict(gato, request) for gato in gatos],
        safe=False
    )

@csrf_exempt
@require_http_methods(["POST"])
def criar_solicitacao_adocao(request):
    data = json_body(request)

    nome = data.get("nome")
    telefone = data.get("telefone")
    email = data.get("email")
    animal = data.get("animal")
    mensagem = data.get("mensagem")

    if not nome or not telefone or not email or not animal:
        return JsonResponse(
            {"erro": "Todos os campos são obrigatórios."},
            status=400
        )

    solicitacao = SolicitacaoAdocao.objects.create(
        nome=nome,
        telefone=telefone,
        email=email,
        animal_interesse=animal,
        mensagem=mensagem,
    )

    return JsonResponse(
        {
            "mensagem": "Solicitação enviada com sucesso.",
            "id": solicitacao.id,
        },
        status=201
    )



# Página da dashboard
@login_required
@ensure_csrf_cookie
def dashboard(request):
    return render(request, "gatos/dashboard.html")

# solicitações de adoção para a dashboard, onde é possível listar todas as solicitações feitas pelos usuários do site
@login_required
@require_http_methods(["GET"])
def dashboard_solicitacoes(request):
    solicitacoes = SolicitacaoAdocao.objects.all().order_by("-data_envio")
    return JsonResponse(
        [solicitacao_to_dict(solicitacao) for solicitacao in solicitacoes],
        safe=False
    )
#detalhe da solicitação de adoção, onde é possível alterar o status ou deletar a solicitação
@login_required
@require_http_methods(["POST", "DELETE"])
def dashboard_solicitacao_detalhe(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoAdocao, id=solicitacao_id)

    if request.method == "DELETE":
        solicitacao.delete()
        return JsonResponse({"mensagem": "Solicitação removida com sucesso."})

    data = json_body(request)
    novo_status = data.get("status")

    status_permitidos = ["nova", "em_analise", "respondida", "recusada"]

    if novo_status not in status_permitidos:
        return JsonResponse(
            {"erro": "Status inválido."},
            status=400
        )

    solicitacao.status = novo_status
    solicitacao.save()

    return JsonResponse(solicitacao_to_dict(solicitacao))

# -----------------------------
# ENDPOINTS DA DASHBOARD - PETS
# -----------------------------

@login_required
@require_http_methods(["GET", "POST"])
def dashboard_pets(request):
    if request.method == "GET":
        pets = Pet.objects.all().order_by("-data_entrada")
        return JsonResponse([pet_to_dict(pet, request) for pet in pets], safe=False)

    nome = request.POST.get("nome")
    sexo = request.POST.get("sexo")
    idade = request.POST.get("idade") or None
    cor = request.POST.get("cor")
    descricao = request.POST.get("descricao")
    status = request.POST.get("status", "disponivel")
    foto = request.FILES.get("foto")

    
    
    
    if not nome or not sexo:
        return JsonResponse(
        {"erro": "Nome e sexo são obrigatórios."},
        status=400
    )

    try:
        foto_url = None

        if foto:
            foto_url = upload_foto_supabase(foto)

        pet = Pet.objects.create(
            nome=nome,
            sexo=sexo,
            idade=idade,
            cor=cor,
            descricao=descricao,
            status=status,
            foto_url=foto_url,
            usuario_cadastro=request.user
        )

        return JsonResponse(pet_to_dict(pet, request), status=201)

    except Exception as erro:
        return JsonResponse(
            {"erro": str(erro)},
            status=500
    )


@login_required
@require_http_methods(["POST", "DELETE"])
def dashboard_pet_detalhe(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == "DELETE":
        pet.delete()
        return JsonResponse({"mensagem": "Gato removido com sucesso."})

    data = request.POST

    pet.nome = data.get("nome", pet.nome)
    pet.sexo = data.get("sexo", pet.sexo)
    pet.idade = data.get("idade") or pet.idade
    pet.cor = data.get("cor", pet.cor)
    pet.descricao = data.get("descricao", pet.descricao)
    pet.status = data.get("status", pet.status)

    if request.FILES.get("foto"):
        pet.foto_url = upload_foto_supabase(request.FILES.get("foto"))

    pet.save()

    return JsonResponse(pet_to_dict(pet, request))


# ----------------------------------
# ENDPOINTS DA DASHBOARD - ADOTANTES
# ----------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def dashboard_adotantes(request):
    if request.method == "GET":
        adotantes = Adotante.objects.all().order_by("nome")
        return JsonResponse(
            [adotante_to_dict(adotante) for adotante in adotantes],
            safe=False
        )

    data = json_body(request)

    cpf = data.get("cpf")
    nome = data.get("nome")

    if not cpf or not nome:
        return JsonResponse(
            {"erro": "CPF e nome são obrigatórios."},
            status=400
        )

    adotante = Adotante.objects.create(
        cpf=cpf,
        nome=nome,
        email=data.get("email"),
        telefone=data.get("telefone"),
        endereco=data.get("endereco"),
    )

    return JsonResponse(adotante_to_dict(adotante), status=201)


@login_required
@require_http_methods(["POST", "DELETE"])
def dashboard_adotante_detalhe(request, cpf):
    adotante = get_object_or_404(Adotante, cpf=cpf)

    if request.method == "DELETE":
        adotante.delete()
        return JsonResponse({"mensagem": "Adotante removido com sucesso."})

    data = json_body(request)

    adotante.nome = data.get("nome", adotante.nome)
    adotante.email = data.get("email", adotante.email)
    adotante.telefone = data.get("telefone", adotante.telefone)
    adotante.endereco = data.get("endereco", adotante.endereco)
    adotante.save()

    return JsonResponse(adotante_to_dict(adotante))


# --------------------------------
# ENDPOINTS DA DASHBOARD - ADOÇÕES
# --------------------------------

@login_required
@require_http_methods(["GET", "POST"])
def dashboard_adocoes(request):
    if request.method == "GET":
        adocoes = Adocao.objects.select_related("pet", "adotante").order_by("-data_adocao")
        return JsonResponse(
            [adocao_to_dict(adocao) for adocao in adocoes],
            safe=False
        )

    data = json_body(request)

    pet_id = data.get("pet_id")
    adotante_cpf = data.get("adotante_cpf")
    observacoes = data.get("observacoes")

    if not pet_id or not adotante_cpf:
        return JsonResponse(
            {"erro": "Gato e adotante são obrigatórios."},
            status=400
        )

    pet = get_object_or_404(Pet, id=pet_id)
    adotante = get_object_or_404(Adotante, cpf=adotante_cpf)

    if pet.status == "adotado":
        return JsonResponse(
            {"erro": "Este gato já está marcado como adotado."},
            status=400
        )

    adocao = Adocao.objects.create(
        pet=pet,
        adotante=adotante,
        observacoes=observacoes,
    )

    return JsonResponse(adocao_to_dict(adocao), status=201)


@login_required
@require_http_methods(["DELETE"])
def dashboard_adocao_detalhe(request, adocao_id):
    adocao = get_object_or_404(Adocao, id=adocao_id)

    pet = adocao.pet
    adocao.delete()

    pet.status = "disponivel"
    pet.save()

    return JsonResponse({"mensagem": "Adoção removida com sucesso."})

# função para enviar as fotos para o Supabase - ainda em teste
def upload_foto_supabase(arquivo):
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    bucket = os.getenv("SUPABASE_BUCKET", "fotos-gatos")

    if not supabase_url:
        raise Exception("SUPABASE_URL não configurada.")

    if not supabase_key:
        raise Exception("SUPABASE_SERVICE_ROLE_KEY não configurada.")

    if not bucket:
        raise Exception("SUPABASE_BUCKET não configurado.")

    supabase = create_client(supabase_url, supabase_key)

    extensao = arquivo.name.split(".")[-1].lower()
    nome_arquivo = f"gatos/{uuid.uuid4()}.{extensao}"

    conteudo = arquivo.read()

    supabase.storage.from_(bucket).upload(
        nome_arquivo,
        conteudo,
        {
            "content-type": arquivo.content_type,
        }
    )

    public_url = supabase.storage.from_(bucket).get_public_url(nome_arquivo)

    return public_url