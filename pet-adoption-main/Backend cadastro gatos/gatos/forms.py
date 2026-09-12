from django.db import models

class Gato(models.Model):
    nome = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="Disponível")
    # ... outros campos do gato ...

    def __str__(self):
        return self.nome

class Adotante(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=14, unique=True)

    def __str__(self):
        return self.nome

class Adocao(models.Model):
    # Relacionamentos (Chaves Estrangeiras)
    gato = models.ForeignKey(Gato, on_delete=models.CASCADE)
    adotante = models.ForeignKey(Adotante, on_delete=models.CASCADE)
    data_adocao = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Adoção"
        verbose_name_plural = "Adoções"

    def __str__(self):
        return f"{self.adotante} adotou {self.gato}"
        