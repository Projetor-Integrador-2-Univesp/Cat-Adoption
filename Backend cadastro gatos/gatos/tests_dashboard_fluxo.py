"""Testes das regras administrativas de intenções, visitas e adoções."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Adocao, Interessado, Interesse, Pet, Visita


class FluxoAdministrativoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username="staff_teste", password="senha_de_teste", is_staff=True)
        cls.visitante = User.objects.create_user(username="visitante_teste", password="senha_de_teste")
        cls.pet = Pet.objects.create(
            nome="Gato Teste", sexo="M", status="disponivel", usuario_cadastro=cls.admin
        )
        cls.interessado = Interessado.objects.create(nome="Pessoa Teste", tipo_residencia="casa")
        cls.interesse = Interesse.objects.create(interessado=cls.interessado, pet=cls.pet)
        cls.visita = Visita.objects.create(
            interesse=cls.interesse, data_hora=timezone.now() + timedelta(days=1)
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_atualizar_status_da_intencao(self):
        resposta = self.client.post(
            reverse("dashboard_interesse_status", args=[self.interesse.pk]),
            {"status": "aprovado"},
        )
        self.assertEqual(resposta.status_code, 200)
        self.interesse.refresh_from_db()
        self.assertEqual(self.interesse.status, "aprovado")

    def test_atualizar_status_da_visita(self):
        resposta = self.client.post(
            reverse("dashboard_visita_status", args=[self.visita.pk]),
            {"status": "realizada"},
        )
        self.assertEqual(resposta.status_code, 200)
        self.visita.refresh_from_db()
        self.assertEqual(self.visita.status, "realizada")

    def test_adocao_exige_intencao_aprovada(self):
        resposta = self.client.post(
            reverse("dashboard_registrar_adocao"), {"interesse_id": self.interesse.pk}
        )
        self.assertEqual(resposta.status_code, 409)
        self.assertFalse(Adocao.objects.exists())

    def test_adocao_marca_gato_e_bloqueia_duplicidade(self):
        self.interesse.status = "aprovado"
        self.interesse.save(update_fields=["status"])
        url = reverse("dashboard_registrar_adocao")
        resposta = self.client.post(url, {"interesse_id": self.interesse.pk})
        self.assertEqual(resposta.status_code, 201)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.status, "adotado")
        self.assertEqual(Adocao.objects.filter(interesse=self.interesse).count(), 1)
        resposta2 = self.client.post(url, {"interesse_id": self.interesse.pk})
        self.assertEqual(resposta2.status_code, 409)
        self.assertEqual(Adocao.objects.count(), 1)

    def test_usuariocomum_nao_pode_alterar_status(self):
        self.client.force_login(self.visitante)
        resposta = self.client.post(
            reverse("dashboard_interesse_status", args=[self.interesse.pk]),
            {"status": "aprovado"},
        )
        self.assertEqual(resposta.status_code, 403)
