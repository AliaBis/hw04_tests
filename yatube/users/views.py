from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.shortcuts import render
from .forms import CreationForm, ChangeForm, PasswordReset


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    form_class = ChangeForm
    template_name = 'users/password_change.html'


class PasswordReset(PasswordResetView):
    form_class = PasswordReset
    template_name = 'users/password_reset_form.html'


def Done(request):
    template = 'users/password_change_done.html'
    return render(request, template)