from django.contrib import admin
from .models import Pet, Interesse, Interessado, Visita, Adocao

class PetAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sexo', 'cor', 'status', 'data_entrada')
    list_filter = ('status', 'sexo')
    search_fields = ('nome', 'cor',)

class InteressadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'email', 'telefone', 'tipo_residencia')
    search_fields = ('nome', 'cpf', 'email')

class InteresseAdmin(admin.ModelAdmin):
    list_display = ('interessado', 'pet', 'data_interesse', 'status')
    list_filter = ('status', 'data_interesse')
    search_fields = ('interessado_nome', 'pet_nome')

class VisitaAdmin(admin.ModelAdmin):
    list_display = ('interesse', 'data_hora', 'status')
    list_filter = ('status', 'data_hora')

class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('interesse', 'data_adocao')
    list_filter = ('data_adocao',)

# Registar os modelos no painel Admin
admin.site.register(Pet, PetAdmin)
admin.site.register(Interessado, InteressadoAdmin)
admin.site.register(Interesse, InteresseAdmin)
admin.site.register(Visita, VisitaAdmin)
admin.site.register(Adocao, AdocaoAdmin)