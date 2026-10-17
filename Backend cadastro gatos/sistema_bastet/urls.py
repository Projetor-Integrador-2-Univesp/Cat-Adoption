from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from gatos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/gatos/', views.listar_gatos),
    path('api/intencoes/', views.registrar_intencao),
    path('api/intencoes/por-telefone/', views.localizar_intencoes_por_telefone),
    path('api/visitas/', views.solicitar_visita),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)