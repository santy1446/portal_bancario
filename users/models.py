from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Rol(models.Model):
    descripcion = models.CharField(max_length=30)

    def __str__(self):
        return self.descripcion

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    rol = models.OneToOneField(Rol, on_delete=models.PROTECT)

    class Meta:
        permissions = (("listarusuarios", "listarusuarios"),)   
