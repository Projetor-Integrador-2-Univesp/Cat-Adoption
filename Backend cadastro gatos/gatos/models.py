from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Pet(models.Model):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]

    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('em_analise', 'Em análise'),
        ('adotado', 'Adotado'),
    ]

    foto = models.URLField(max_length=500, null=True, blank=True)
    nome = models.CharField(max_length=100, null=True, blank=True)
    data_entrada = models.DateField(default=timezone.now)
    idade = models.IntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    cor = models.CharField(max_length=50, null=True, blank=True)
    descricao = models.TextField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')

    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pets_cadastrados')

    def __str__(self):
        return f"{self.nome} ({self.status})"

class Interessado(models.Model):
    TIPO_RESIDENCIA_CHOICES = [('apartamento', 'Apartamento'), ('casa', 'Casa')]
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, help_text="000.000.000-00")
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    tipo_residencia = models.CharField(max_length=20, choices=TIPO_RESIDENCIA_CHOICES)

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

class Interesse(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em análise'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
    ]

    interessado = models.ForeignKey(Interessado, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    data_interesse = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pendente')
    mensagem = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.interessado.nome} > {self.pet.nome}"

class Visita(models.Model):
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('pendente', 'Pendente')
    ]

    interesse = models.ForeignKey(Interesse, on_delete=models.CASCADE)
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Visita - {self.interesse}"

class Adocao(models.Model):
    interesse = models.OneToOneField(Interesse, on_delete=models.CASCADE, null=True, blank=True)
    data_adocao = models.DateField(default=timezone.now)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Adoção - {self.interesse}"