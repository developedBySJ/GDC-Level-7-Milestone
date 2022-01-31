
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
# Create your views here.


class CustomUserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

        widgets = {
            "username": forms.TextInput(attrs={"class": "input mb-4", }),
            "password1": forms.PasswordInput(attrs={"class": "input mb-4"}),
            "password2": forms.PasswordInput(attrs={"class": "input mb-4"}),
        }


class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]

        widgets = {
            "username": forms.TextInput(attrs={"class": "input mb-4", }),
            "password": forms.PasswordInput(attrs={"class": "input mb-4"}),
        }


class UserLoginView(LoginView):
    template_name = 'user_login.html'
    form_class = CustomLoginForm


class UserCreateView(CreateView):
    form_class = CustomUserCreateForm
    template_name = "user_create.html"
    success_url = "/user/login"
