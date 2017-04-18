from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Ignore this; this form is just for testing purposes
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class Food(models.Model):
    class Meta:
        unique_together = (('food_name', 'quantity'),)
    food_name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    date_listed = models.DateField(auto_now=True, auto_now_add=False)
    FOOD_TYPES = (
        ('VEGE', 'Vegetables'),
        ('SEAFOOD', 'Seafood'),
        ('MEAT', 'Meat'),
        ('COOKED', 'Cooked'),
        ('FRUIT', 'Fruit'),
        ('BAKERY', 'Bakery Items'),
        ('PASTA_RICE', 'Pasta & Rice'),
        ('DRIED', 'Dried food'),
        ('OTHER', 'Other')
    )
    food_type = models.CharField(choices=FOOD_TYPES,default='OTHER',max_length=50)
    ALLERGENS = (
        ('NUTS', 'Nuts'),
        ('GLUTEN', 'Gluten'),
        ('NON_VEGAN', 'Non-Vegan'),
        ('SEAFOOD', 'Seafood'),
        ('EGGS', 'Eggs'),
        ('NONE', 'None'),
    )
    allergens = models.CharField(choices=ALLERGENS,default='NONE',max_length=50)
    STATUS = (
        ('AVAILABLE', 'Available'),
        ('RESERVED', 'Reserved'),
        ('UNAVAILABLE', 'Unavailable')
    )
    status = models.CharField(choices=STATUS,default='AVAILABLE',max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    picture = models.TextField(default='0')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')

    def __str__(self):
        return self.food_name + " " + str(self.quantity)


class Preference(models.Model):
    class Meta:
        unique_together = (('preference', 'preference_user'),)
    FOOD_TYPES = (
        ('VEGE', 'Vegetables'),
        ('SEAFOOD', 'Seafood'),
        ('MEAT', 'Meat'),
        ('COOKED', 'Cooked'),
        ('FRUIT', 'Fruit'),
        ('BAKERY', 'Bakery Items'),
        ('PASTA_RICE', 'Pasta & Rice'),
        ('DRIED', 'Dried food'),
        ('OTHER', 'Other')
    )
    preference = models.CharField(choices=FOOD_TYPES, default='OTHER', max_length=20)
    preference_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preference_user')


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    receiver = models.ForeignKey(User, related_name="receiver")
    msg_content = models.CharField(max_length=500)
    created_at = models.CharField(max_length=50, default=str(datetime.now()))
    read = models.BooleanField(default=False)

    @classmethod
    def create(cls, sender, receiver, msg_content):
        message = cls(sender=sender, receiver=receiver, msg_content=msg_content)
        message.created_at = str(datetime.now())
        return message
