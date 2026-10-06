from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from gatos import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'login/',
        auth_views.LoginView.as_view(template_name='gatos/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    path('dashboard/', views.dashboard, name='dashboard'),

    # Endpoint público usado pelo site
    path('api/gatos/', views.listar_gatos),

    # Endpoints internos da dashboard
    path('api/dashboard/pets/', views.dashboard_pets),
    path('api/dashboard/pets/<int:pet_id>/', views.dashboard_pet_detalhe),

    path('api/dashboard/adotantes/', views.dashboard_adotantes),
    path('api/dashboard/adotantes/<str:cpf>/', views.dashboard_adotante_detalhe),

    path('api/dashboard/adocoes/', views.dashboard_adocoes),
    path('api/dashboard/adocoes/<int:adocao_id>/', views.dashboard_adocao_detalhe),

    path('api/solicitacoes-adocao/', views.criar_solicitacao_adocao),

    path('api/dashboard/solicitacoes/', views.dashboard_solicitacoes),
    path('api/dashboard/solicitacoes/<int:solicitacao_id>/', views.dashboard_solicitacao_detalhe),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)