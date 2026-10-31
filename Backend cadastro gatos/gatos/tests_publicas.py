"""Testes do formulário público e das solicitações de visitas."""

import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Interessado, Interesse, Pet, Visita


class FluxoPublicoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuario = User.objects.create_user(username="admin_publico", password="senha_teste")
        cls.pet = Pet.objects.create(
            nome="Lua", sexo="F", status="disponivel", usuario_cadastro=usuario,
        )

    def enviar_intencao(self, **alteracoes):
        dados = {
            "nome": "Ana Teste", "telefone": "(19) 91234-5678",
            "email": "ana@example.com", "pet_id": self.pet.pk,
            "tipo_residencia": "casa", "rotina": "Moro em casa telada e tenho tempo para cuidar.",
        }
        dados.update(alteracoes)
        return self.client.post(
            reverse("registrar_intencao_publica"),
            json.dumps(dados), content_type="application/json",
        )

    def enviar_visita(self, interesse_id, token, **alteracoes):
        dados = {
            "interesse_id": interesse_id, "token_visita": token,
            "data_hora": (timezone.now() + timedelta(days=2)).isoformat(),
            "observacoes": "Preferência pelo período da tarde.",
        }
        dados.update(alteracoes)
        return self.client.post(
            reverse("solicitar_visita_publica"),
            json.dumps(dados), content_type="application/json",
        )

    def test_intencao_cria_interessado_e_registro(self):
        resposta = self.enviar_intencao()
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(Interessado.objects.count(), 1)
        interesse = Interesse.objects.get()
        self.assertEqual(interesse.pet, self.pet)
        self.assertEqual(interesse.status, "pendente")
        self.assertEqual(interesse.interessado.tipo_residencia, "casa")
        self.assertTrue(resposta.json()["token_visita"])

    def test_nao_aceita_gato_adotado(self):
        self.pet.status = "adotado"
        self.pet.save(update_fields=["status"])
        resposta = self.enviar_intencao()
        self.assertEqual(resposta.status_code, 409)
        self.assertFalse(Interesse.objects.exists())

    def test_intencao_rejeita_residencia_invalida(self):
        resposta = self.enviar_intencao(tipo_residencia="outro")
        self.assertEqual(resposta.status_code, 400)
        self.assertFalse(Interessado.objects.exists())

    def test_visita_com_comprovante_valido(self):
        intencao = self.enviar_intencao().json()
        resposta = self.enviar_visita(intencao["interesse_id"], intencao["token_visita"])
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(Visita.objects.count(), 1)
        self.assertEqual(Visita.objects.get().status, "pendente")

    def test_visita_nao_aceita_comprovante_de_outra_intencao(self):
        primeira = self.enviar_intencao().json()
        segunda = self.enviar_intencao(telefone="(19) 97654-3210").json()
        resposta = self.enviar_visita(segunda["interesse_id"], primeira["token_visita"])
        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(Visita.objects.exists())

    def test_visita_sem_comprovante_e_bloqueada(self):
        intencao = self.enviar_intencao().json()
        resposta = self.enviar_visita(intencao["interesse_id"], "")
        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(Visita.objects.exists())

    def test_visita_duplicada_e_bloqueada(self):
        intencao = self.enviar_intencao().json()
        self.assertEqual(self.enviar_visita(intencao["interesse_id"], intencao["token_visita"]).status_code, 201)
        self.assertEqual(self.enviar_visita(intencao["interesse_id"], intencao["token_visita"]).status_code, 409)
        self.assertEqual(Visita.objects.count(), 1)

    def test_visita_nao_aceita_data_passada(self):
        intencao = self.enviar_intencao().json()
        resposta = self.enviar_visita(
            intencao["interesse_id"], intencao["token_visita"],
            data_hora=(timezone.now() - timedelta(days=1)).isoformat(),
        )
        self.assertEqual(resposta.status_code, 400)
        self.assertFalse(Visita.objects.exists())
