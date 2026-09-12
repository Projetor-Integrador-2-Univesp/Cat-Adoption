from django.db import models
from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# --- 1. MODELO ---
class Pet(models.Model):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('adotado', 'Adotado'),
        ('em_tratamento', 'Em Tratamento'),
    ]

    nome = models.CharField(max_length=100)
    data_entrada = models.DateField(default=timezone.now)
    idade = models.IntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    cor = models.CharField(max_length=50, null=True, blank=True)
    descricao = models.TextField(max_length=500, null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='disponivel'
    )
    
    usuario_cadastro = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name='pets_cadastrados'
    )

    def __str__(self):
        return f"{self.nome} - {self.status}"

# --- 2. FORMULÁRIO ---
class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['nome', 'idade', 'sexo', 'cor', 'descricao', 'status']

# --- 3. VIEW ---
def cadastrar_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.usuario_cadastro = request.user 
            pet.save()
            return redirect('lista_pets') 
    else:
        form = PetForm()
    
    return render(request, 'cadastro_pet.html', {'form': form})