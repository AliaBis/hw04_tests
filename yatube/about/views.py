#  from email.mime import image
#  from django.shortcuts import render
from django.views.generic.base import TemplateView
#  from django.db import models


class AboutAuthorView(TemplateView):
    #  title = models.CharField(max_length=200)
    #  content = models.TextField()
    #  image = models.ImageField(upload_to='photos/')
    template_name = "about/author.html"
    #  В переменной template_name обязательно указывается имя шаблона,
    #  на основе которого будет создана возвращаемая страница
    #  def __str__(self):
    #  return self.image


class AboutTechView(TemplateView):
    #  title = models.CharField(max_length=255)
    #  content = models.TextField()
    #  image = models.ImageField(upload_to='photos/')
    template_name = "about/tech.html"
    #  В переменной template_name обязательно указывается имя шаблона,
    #  на основе которого будет создана возвращаемая страница
    #  def __str__(self):
    #  return self.image
