from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from gatos import (
    views,
    views_dashboard,
    views_dashboard_fluxo,
    views_dashboard_pets,
    views_dashboard_relacoes,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="gatos/login.html",
            redirect_authenticated_user=True,
            next_page="dashboard",
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("dashboard/", views_dashboard.dashboard, name="dashboard"),
    path("api/dashboard/pets/", views_dashboard_pets.dashboard_pets, name="dashboard_pets"),
    path(
        "api/dashboard/pets/<int:pet_id>/",
        views_dashboard_pets.dashboard_pet_detalhe,
        name="dashboard_pet_detalhe",
    ),
    path(
        "api/dashboard/interessados/",
        views_dashboard_relacoes.listar_interessados,
        name="dashboard_interessados",
    ),
    path(
        "api/dashboard/interesses/",
        views_dashboard_relacoes.listar_interesses,
        name="dashboard_interesses",
    ),
    path(
        "api/dashboard/visitas/",
        views_dashboard_relacoes.listar_visitas,
        name="dashboard_visitas",
    ),
    path(
        "api/dashboard/adocoes/",
        views_dashboard_relacoes.listar_adocoes,
        name="dashboard_adocoes",
    ),
    path(
        "api/dashboard/interesses/<int:interesse_id>/status/",
        views_dashboard_fluxo.atualizar_status_interesse,
        name="dashboard_interesse_status",
    ),
    path(
        "api/dashboard/visitas/<int:visita_id>/status/",
        views_dashboard_fluxo.atualizar_status_visita,
        name="dashboard_visita_status",
    ),
    path(
        "api/dashboard/adocoes/registrar/",
        views_dashboard_fluxo.registrar_adocao,
        name="dashboard_registrar_adocao",
    ),
    path("api/gatos/", views.listar_gatos),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
