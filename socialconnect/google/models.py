from django.db import models

# Create your models here.
class User(models.Model):
    firstname = models.CharField(max_length = 150)
    lastname = models.CharField(max_length=100)
    mailid = models.EmailField(max_length=254)
    password = models.CharField(max_length = 150)
    phone = models.IntegerField()