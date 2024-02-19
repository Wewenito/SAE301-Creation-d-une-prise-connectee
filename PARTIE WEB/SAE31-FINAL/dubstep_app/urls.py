from django.urls import path
from . import views
from .views import Mqtt, Jukebox
from django.contrib.auth.decorators import user_passes_test, login_required


urlpatterns = [
    path('index/', views.index),

    path('', login_required(Mqtt.as_view(), login_url='/login_user')),
    path('mainpage', login_required(Mqtt.as_view(), login_url='/login_user')),
    path('mainpage/', login_required(Mqtt.as_view(), login_url='/login_user')),

    path('login_user',views.login_user),
    path('logout_user', views.logout_user),

    path('plages/', views.plages),
    path('plages', views.plages),
    path('traitement/', views.traitement),
    path('traitement', views.traitement),

    path('delete/<int:id>/', views.delete),
    path('delete/<int:id>', views.delete),

    path('graphique', views.graphique),
    path('graphique/', views.graphique),

    path('jukebox', login_required(Jukebox.as_view(), login_url='/login_user')),
    path('jukebox/', login_required(Jukebox.as_view(), login_url='/login_user')),

]
