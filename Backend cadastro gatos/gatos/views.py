from django.http import JsonResponse
from .models import Pet

def listar_gatos(request):
    gatos = Pet.objects.filter(status='disponivel').values(
        'id', 'idade', 'sexo', 'cor', 'descricao', 'foto'
    )
    return JsonResponse(list(gatos), safe=False)