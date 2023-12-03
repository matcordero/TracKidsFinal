from django.urls import path,include
from rest_framework import routers

from .views import *
router = routers.DefaultRouter()

urlpatterns = [
    path('',include(router.urls)),
    #path('mi_endpoint', mi_endpoint, name='mi_endpoint'),
    #path('encriptar/<str:dato>', encriptar, name='login'),
    
    path('login',login,name='login'),
    path('getUsuario',getUsuario,name='getUsuario'),
    path('getProyectos',getProyectos,name='getProyectos'),
    path('getAllProyectos',getAllProyectos,name='getAllProyectos'),
    path('getAllSongs',getAllSongs,name='getAllSongs'),
    path('getOneSong',getOneSong,name='getOneSong'),
    path('cancionSemanaYoutube',cancionSemanaYoutube,name='cancionSemanaYoutube'),
    path('proyectoToSong',proyectoToSong,name='proyectoToSong'),
    path('modificarProyecto',modificarProyecto,name='modificarProyecto'),
    path('register',register,name='register'),
    path('obtenerSeparacionPorYoutube',obtenerSeparacionPorYoutube,name='obtenerSeparacionPorYoutube'),
    path('obtenerSeparacionPorAudio',obtenerSeparacionPorAudio,name='obtenerSeparacionPorAudio'),
]


