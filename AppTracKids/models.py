from django.utils import timezone
from django.db import models

# Create your models here.
class Usuario(models.Model):
    name = models.CharField(max_length=100)
    birtDate = models.DateTimeField(default=timezone.now)
    email = models.EmailField(primary_key=True)
    password = models.TextField()
    icon = models.TextField()
    keyValidate = models.CharField(max_length=100, null=True, blank=True)
    
    
class Project(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey('Usuario',on_delete=models.DO_NOTHING)
    titulo = models.TextField(default="")
    imagen = models.TextField(default="")
    vocals = models.TextField(default="")
    other = models.TextField(default="")
    drums = models.TextField(default="")
    bass = models.TextField(default="")
    