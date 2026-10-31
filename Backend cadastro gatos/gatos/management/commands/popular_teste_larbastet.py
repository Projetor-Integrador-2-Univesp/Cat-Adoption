"""Cria registros fictícios no SQLite local para testar o painel administrativo."""

from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from gatos.models import Adocao, Interessado, Interesse, Pet, Visita


CASOS = [
    # Gato, interessado, intenção e visita com diferentes estados para teste.
    ("TESTE LOCAL - Lua", "F", "Cinza", "TESTE LOCAL - Ana", "ana-teste@example.com", "casa", "pendente", "pendente", 2),
    ("TESTE LOCAL - Nino", "M", "Preto e branco", "TESTE LOCAL - Bruno", "bruno-teste@example.com", "apartamento", "em_analise", "agendada", 4),
    ("TESTE LOCAL - Mel", "F", "Caramelo", "TESTE LOCAL - Carla", "carla-teste@example.com", "casa", "aprovado", "realizada", -2),
    ("TESTE LOCAL - Bento", "M", "Laranja", "TESTE LOCAL - Diego", "diego-teste@example.com", "apartamento", "recusado", "cancelada", 1),
    ("TESTE LOCAL - Amora", "F", "Tricolor", "TESTE LOCAL - Elisa", "elisa-teste@example.com", "casa", "aprovado", "realizada", -5),
    ("TESTE LOCAL - Tito", "M", "Branco", "TESTE LOCAL - Felipe", "felipe-teste@example.com", "apartamento", "pendente", None, 0),
]


class Command(BaseCommand):
    help = "Cria gatos, interessados, intencoes, visitas e uma adocao ficticios no SQLite local."

    def handle(self, *args, **options):
        # O comando só pode modificar o banco SQLite reservado aos testes.
        if settings.SETTINGS_MODULE != "sistema_bastet.settings_recuperacao":
            raise CommandError("Abortado: utilize --settings=sistema_bastet.settings_recuperacao.")
        banco = settings.DATABASES["default"]
        if (banco.get("ENGINE") != "django.db.backends.sqlite3"
                or Path(str(banco.get("NAME", ""))).name != "db_recuperacao.sqlite3"):
            raise CommandError("Abortado: banco nao e o SQLite isolado db_recuperacao.sqlite3.")

        responsavel = get_user_model().objects.filter(is_staff=True).order_by("pk").first()
        if responsavel is None:
            raise CommandError(
                "Nenhum usuario staff no banco de testes. Execute primeiro: "
                "python manage.py createsuperuser --settings=sistema_bastet.settings_recuperacao"
            )

        agora = timezone.now()
        contador = {"gatos": 0, "interessados": 0, "intencoes": 0, "visitas": 0, "adocoes": 0}
        with transaction.atomic():
            for (nome_gato, sexo, cor, nome_pessoa, email, moradia,
                 status_intencao, status_visita, deslocamento) in CASOS:
                gato, novo = Pet.objects.get_or_create(
                    nome=nome_gato,
                    defaults={
                        "sexo": sexo, "cor": cor, "idade": 2,
                        "descricao": "Registro ficticio para testar a dashboard local.",
                        "status": "disponivel", "usuario_cadastro": responsavel,
                    },
                )
                contador["gatos"] += int(novo)

                pessoa, novo = Interessado.objects.get_or_create(
                    nome=nome_pessoa,
                    defaults={
                        "email": email,
                        "telefone": "(00) 00000-0000",
                        "tipo_residencia": moradia,
                        "endereco": "ENDERECO FICTICIO - NAO UTILIZAR",
                    },
                )
                contador["interessados"] += int(novo)

                intencao, novo = Interesse.objects.get_or_create(
                    interessado=pessoa, pet=gato,
                    defaults={
                        "status": status_intencao,
                        "mensagem": "Intencao ficticia: gostaria de adotar este gato.",
                    },
                )
                contador["intencoes"] += int(novo)

                if status_visita is not None:
                    # Mantém o status modificado em execuções anteriores.
                    if not Visita.objects.filter(interesse=intencao).exists():
                        Visita.objects.create(
                            interesse=intencao,
                            data_hora=agora + timedelta(days=deslocamento),
                            status=status_visita,
                            observacoes="Visita ficticia criada para testar status.",
                        )
                        contador["visitas"] += 1

                # Amora já possui adoção; Mel permanece disponível para o teste de registro.
                if nome_gato == "TESTE LOCAL - Amora":
                    _, novo = Adocao.objects.get_or_create(
                        interesse=intencao,
                        defaults={
                            "data_adocao": timezone.localdate() - timedelta(days=1),
                            "observacoes": "Adocao ficticia para testes locais.",
                        },
                    )
                    contador["adocoes"] += int(novo)
                    if gato.status != "adotado":
                        gato.status = "adotado"
                        gato.save(update_fields=["status"])

        self.stdout.write(self.style.SUCCESS("Dados ficticios preparados apenas em db_recuperacao.sqlite3."))
        self.stdout.write("Casos disponiveis: 6 gatos, 6 interessados, 6 intencoes, 5 visitas, 1 adocao.")
        self.stdout.write("Criados nesta execucao: " + ", ".join(f"{k}: {v}" for k, v in contador.items()))
        self.stdout.write("Teste: altere o status da intencao da Lua e da visita do Nino.")
        self.stdout.write("Teste: registre a adocao da Mel; a Amora ja foi adotada.")
        self.stdout.write("O comando nao redefine status modificados em execucoes anteriores.")
