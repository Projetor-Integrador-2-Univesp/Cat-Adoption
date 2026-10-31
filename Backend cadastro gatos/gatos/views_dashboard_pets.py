"""Cadastro e gerenciamento de gatos no painel administrativo."""

import os
import uuid
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from PIL import Image, UnidentifiedImageError

from .models import Adocao, Interesse, Pet


MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_FORMATS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "WEBP": ("webp", "image/webp"),
}


class PetInputError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def _pet_dict(pet):
    return {
        "id": pet.pk,
        "nome": pet.nome or "Sem nome",
        "idade": pet.idade,
        "sexo": pet.sexo,
        "sexo_display": pet.get_sexo_display(),
        "cor": pet.cor or "",
        "descricao": pet.descricao or "",
        "status": pet.status,
        "status_display": pet.get_status_display(),
        "data_entrada": pet.data_entrada.isoformat() if pet.data_entrada else None,
        "foto": pet.foto or "",
    }


def _validate_data(post, pet=None):
    def required_or_existing(field, current=""):
        return str(post.get(field, current) or "").strip()

    name = required_or_existing("nome", pet.nome if pet else "")
    sex = required_or_existing("sexo", pet.sexo if pet else "")
    status = required_or_existing("status", pet.status if pet else "disponivel")
    cor = required_or_existing("cor", pet.cor if pet else "")
    descricao = required_or_existing("descricao", pet.descricao if pet else "")
    raw_age = required_or_existing("idade", pet.idade if pet and pet.idade is not None else "")

    if not name or len(name) > 100:
        raise PetInputError("Informe um nome com até 100 caracteres.")
    if sex not in dict(Pet.SEXO_CHOICES):
        raise PetInputError("Sexo inválido.")
    if status not in dict(Pet.STATUS_CHOICES):
        raise PetInputError("Status inválido.")
    if len(cor) > 50 or len(descricao) > 500:
        raise PetInputError("Cor ou descrição ultrapassa o limite permitido.")
    if raw_age:
        try:
            idade = int(raw_age)
        except (TypeError, ValueError):
            raise PetInputError("A idade precisa ser um número inteiro.") from None
        if not 0 <= idade <= 99:
            raise PetInputError("A idade deve estar entre 0 e 99 anos.")
    else:
        idade = None
    return {
        "nome": name,
        "sexo": sex,
        "status": status,
        "cor": cor,
        "descricao": descricao,
        "idade": idade,
    }


def _upload_photo(arquivo):
    """Envia a imagem para o Supabase Storage e retorna a URL pública."""
    if not arquivo:
        return None

    if arquivo.size > MAX_IMAGE_BYTES:
        raise PetInputError("A imagem deve ter no máximo 5 MB.")

    raw = arquivo.read(MAX_IMAGE_BYTES + 1)
    if len(raw) > MAX_IMAGE_BYTES:
        raise PetInputError("A imagem deve ter no máximo 5 MB.")
    try:
        with Image.open(BytesIO(raw)) as img:
            image_format = img.format
            img.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise PetInputError("Arquivo inválido. Envie JPG, PNG ou WebP.") from None

    if image_format not in ALLOWED_FORMATS:
        raise PetInputError("Formato de imagem não permitido. Use JPG, PNG ou WebP.")

    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    bucket = os.environ.get("SUPABASE_BUCKET", "fotos-gatos")

    if not supabase_url or not service_key:
        raise PetInputError(
            "Upload indisponível: configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no ambiente.",
            status=503,
        )
    parsed = urlsplit(supabase_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise PetInputError("SUPABASE_URL precisa ser uma URL HTTPS válida.", status=503)

    suffix, content_type = ALLOWED_FORMATS[image_format]
    path = f"gatos/{uuid.uuid4().hex}.{suffix}"
    upload_url = f"{supabase_url}/storage/v1/object/{quote(bucket, safe='')}/{quote(path, safe='/')}"
    request = Request(
        upload_url,
        data=raw,
        headers={
            "Authorization": f"Bearer {service_key}",
            "apikey": service_key,
            "Content-Type": content_type,
            "x-upsert": "false",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as result:
            if not 200 <= result.status < 300:
                raise PetInputError("Falha ao enviar a foto para o Storage.", status=502)
    except (HTTPError, URLError, TimeoutError, OSError):
        # Evita expor detalhes internos nas mensagens de erro do Storage.
        raise PetInputError("Falha ao enviar a foto para o Storage.", status=502) from None

    return f"{supabase_url}/storage/v1/object/public/{quote(bucket, safe='')}/{quote(path, safe='/')}"


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def dashboard_pets(request):
    if not request.user.is_staff:
        return JsonResponse({"erro": "Acesso restrito à administração."}, status=403)

    if request.method == "GET":
        pets = Pet.objects.all().order_by("-data_entrada", "-pk")
        return JsonResponse([_pet_dict(pet) for pet in pets], safe=False)

    try:
        values = _validate_data(request.POST)
        photo_url = _upload_photo(request.FILES.get("foto"))
    except PetInputError as error:
        return JsonResponse({"erro": str(error)}, status=error.status)

    pet = Pet.objects.create(**values, foto=photo_url, usuario_cadastro=request.user)
    return JsonResponse(_pet_dict(pet), status=201)


@login_required(login_url="login")
@require_http_methods(["POST", "DELETE"])
def dashboard_pet_detalhe(request, pet_id):
    if not request.user.is_staff:
        return JsonResponse({"erro": "Acesso restrito à administração."}, status=403)

    pet = get_object_or_404(Pet, pk=pet_id)

    if request.method == "DELETE":
        # Evita excluir interesses, visitas e adoções por cascata.
        if Interesse.objects.filter(pet_id=pet.pk).exists():
            return JsonResponse(
                {"erro": "Este gato possui interesses registrados. Não é seguro excluí-lo."},
                status=409,
            )
        pet.delete()
        return JsonResponse({"mensagem": "Gato removido com sucesso."})

    try:
        values = _validate_data(request.POST, pet)
        photo_url = _upload_photo(request.FILES.get("foto"))
    except PetInputError as error:
        return JsonResponse({"erro": str(error)}, status=error.status)

    # Uma adoção registrada impede que o gato volte a ficar disponível.
    if values["status"] != "adotado" and Adocao.objects.filter(interesse__pet_id=pet.pk).exists():
        return JsonResponse(
            {"erro": "Este gato já possui adoção registrada e deve permanecer como adotado."},
            status=409,
        )

    for field, value in values.items():
        setattr(pet, field, value)
    if photo_url:
        pet.foto = photo_url
    pet.save()
    return JsonResponse(_pet_dict(pet))
