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
        ('adotado', 'Adotado'),
        ('em_tratamento', 'Em Tratamento'),
    ]

    foto = models.ImageField(upload_to='fotos_pets/', null=True, blank=True)
    data_entrada = models.DateField(default=timezone.now)
    idade = models.IntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    cor = models.CharField(max_length=50, null=True, blank=True)
    descricao = models.TextField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    
    usuario_cadastro = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pets_cadastrados')

    def __str__(self):
        return f"Pet #{self.pk} ({self.status})"

class Adotante(models.Model):
    cpf = models.CharField(max_length=14, primary_key=True, help_text="000.000.000-00")
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

    class Meta:
        verbose_name = "Adotante"
        verbose_name_plural = "Adotantes"

class Adocao(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adocoes')
    adotante = models.ForeignKey(Adotante, on_delete=models.CASCADE, related_name='pets_adotados')
    data_adocao = models.DateField(default=timezone.now)
    observacoes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.pet.status = 'adotado'
        self.pet.save()

    def __str__(self):
        return f"{self.pet.nome} adotado por {self.adotante.nome}"

    class Meta:
        verbose_name = "Adoção"
        verbose_name_plural = "Adoções"