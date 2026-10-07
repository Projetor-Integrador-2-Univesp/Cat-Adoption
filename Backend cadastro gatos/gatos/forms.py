from django import forms
from .models import Pet, Interessado, Interesse, Visita, Adocao

class PetForm(forms.ModelForm):
    class Meta:
            model = Pet
            fields = [
                'foto',
                'nome',
                'data_entrada',
                'idade',
                'sexo',
                'cor',
                'descricao',
                'status',
            ]

class InteressadoForm(forms.ModelForm):
    class Meta:
        model = Interessado
        fields = [
            'nome',
            'cpf',
            'email',
            'telefone',
            'endereco',
            'tipo_residencia'
        ]

class InteresseForm(forms.ModelForm):
    class Meta:
        model = Interesse
        fields = [
            'interessado',
            'pet',
            'data_interesse',
            'status',
            'mensagem',
        ]

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = [
            'interesse',
            'data_hora',
            'status',
            'observacoes',
        ]

class AdocaoForm(forms.ModelForm):
    class Meta:
        model = Adocao
        fields = [
            'interesse',
            'data_adocao',
            'observacoes',
        ]
