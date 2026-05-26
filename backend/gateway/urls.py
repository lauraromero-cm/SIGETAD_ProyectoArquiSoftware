from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health),
    path('login/', views.login),
    path('register/', views.register_candidate),
    path('usuarios/', views.usuarios),
    path('usuarios/<int:id_usuario>/estado/', views.usuario_estado),
    path('usuarios/<int:id_usuario>/delete/', views.usuario_delete),
    path('vacantes/', views.vacantes),
    path('vacantes/<int:id_vacante>/', views.vacante_detail),
    path('vacantes/<int:id_vacante>/cerrar/', views.vacante_cerrar),
    path('candidatos/', views.candidatos),
    path('candidatos/me/', views.candidato_me),
    path('postulaciones/', views.postulaciones),
    path('postulaciones/<int:id_postulacion>/', views.postulacion_detail),
    path('postulaciones/<int:id_postulacion>/estado/', views.postulacion_estado),
    path('evaluaciones/', views.evaluaciones),
    path('historial/', views.historial),
]
