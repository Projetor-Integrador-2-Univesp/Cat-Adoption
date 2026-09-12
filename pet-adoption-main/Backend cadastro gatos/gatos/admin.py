from django.contrib import admin
from .models import Pet, Adotante, Adocao

# Configuração para o Pet aparecer com mais detalhes na lista
class PetAdmin(admin.ModelAdmin):
    list_display = ('sexo', 'cor', 'status', 'data_entrada')
    list_filter = ('status', 'sexo')
    search_fields = ('cor',)

# Configuração para o Adotante aparecer com CPF na lista
class AdotanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'email', 'telefone')
    search_fields = ('nome', 'cpf')

# Configuração para a Adoção
class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('pet', 'adotante', 'data_adocao')
    list_filter = ('data_adocao',)

# Registar os modelos no painel Admin
admin.site.register(Pet, PetAdmin)
admin.site.register(Adotante, AdotanteAdmin)
admin.site.register(Adocao, AdocaoAdmin)