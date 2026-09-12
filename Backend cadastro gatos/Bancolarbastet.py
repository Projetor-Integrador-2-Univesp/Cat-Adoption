from django.db import models

class UsuarioSistema(models.Model):
    # O Django cria um ID automático, mas definiremos conforme o diagrama
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    senha = models.CharField(max_length=128)  # No Django real, usaríamos AbstractUser

    def __str__(self):
        return self.nome

class Pet(models.Model):
    id_pet = models.AutoField(primary_key=True)
    data_entrada = models.DateField()
    idade = models.IntegerField()
    # Usando choices para campos numéricos que representam categorias (ex: 1: Macho, 2: Fêmea)
    sexo = models.IntegerField() 
    cor = models.CharField(max_length=50)
    descricao = models.TextField()
    status = models.IntegerField()
    # Relacionamento (1,n) com UsuarioSistema
    usuario_sistema = models.ForeignKey(UsuarioSistema, on_delete=models.PROTECT)

    def __str__(self):
        return f"Pet {self.id_pet} - {self.cor}"

class Adotante(models.Model):
    cpf = models.CharField(max_length=14, primary_key=True)
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    endereco = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome

class Adocao(models.Model):
    id_adocao = models.AutoField(primary_key=True)
    data_adocao = models.DateField()
    obs = models.TextField(blank=True, null=True)
    termo_compromisso = models.DecimalField(max_digits=10, decimal_digits=2)
    
    # Relacionamentos
    # OneToOneField garante que um pet só possa estar em uma adoção (conforme o 0,1 no diagrama)
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE)
    adotante = models.ForeignKey(Adotante, on_delete=models.CASCADE)
    usuario_sistema = models.ForeignKey(UsuarioSistema, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Adoções"
    
    #python manage.py makemigrations
    #python manage.py migrate
