from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
        username = forms.CharField(max_length=150, label="Nombre de Usuario",
                                    widget = forms.TextInput(attrs={'class' : 'form-control'}))
        first_name = forms.CharField(max_length=150, label="Nombre",
                                    widget = forms.TextInput(attrs={'class' : 'form-control'}))
        last_name = forms.CharField(max_length=150, label="Apellido",
                                    widget = forms.TextInput(attrs={'class' : 'form-control'}))
        email = forms.EmailField(max_length=200, label="Correo Electrónico",
                                    widget = forms.TextInput(attrs={'class': 'form-control'}))
        password1 = forms.CharField(max_length=100, label="Contraseña",
                                     widget = forms.PasswordInput(attrs={'class': 'form-control'}))
        password2 = forms.CharField(max_length=100, label="Confirme la Contraseña",
                                     widget = forms.PasswordInput(attrs={'class': 'form-control'}))

        class Meta:
            model = User
            fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


