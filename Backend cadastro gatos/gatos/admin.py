from django.contrib import admin
from .models import Pet, Interesse, Interessado, Visita, Adocao

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sexo', 'cor', 'status', 'data_entrada')
    list_filter = ('status', 'sexo')
    search_fields = ('nome', 'cor',)

@admin.register(Interessado)
class InteressadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'email', 'telefone', 'tipo_residencia')
    search_fields = ('nome', 'cpf', 'email', 'telefone')

@admin.register(Interesse)
class InteresseAdmin(admin.ModelAdmin):
    list_display = ('interessado', 'pet', 'data_interesse', 'status')
    list_filter = ('status', 'data_interesse')
    search_fields = ('interessado_nome', 'pet_nome', 'interessado_cpf')

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'get_interessado', 'get_pet', 'status')
    list_filter = ('status', 'data_hora')
    search_fields = (
        'interesse__interessado__nome',
        'interesse__interessado__cpf',
        'interesse__pet__nome',
    )
    list_select_related = (
        'interesse',
        'interesse__interessado',
        'interesse__pet',
    )
    date_hierarchy = 'data_hora'
    ordering = ('data_hora',)

    @admin.display(description='Interessado')
    def get_interessado(self, obj):
        return obj.interesse.interessado.nome

    @admin.display(description='Gato')
    def get_pet(self, obj):
        return obj.interesse.pet.nome

class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('interesse', 'data_adocao')
    list_filter = ('data_adocao',)