from email.policy import default
from pyexpat import model
from telnetlib import Telnet
from venv import create
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique= True, null=True)
    bio = models.TextField(null= True)

    avatar = models.ImageField(null= True, default="avatar.svg")

  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

#To define a one to many relationship in Django models 
#you use the ForeignKey data type on the model that has the many records 
class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null= True)       #One user has many rooms but one room belongs to one user
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null= True)     #one topic has many rooms but one room belongs to one user.
    name = models.CharField(max_length=200)
    description = models.TextField(null= True, blank=True)
    participants= models.ManyToManyField(User, related_name = 'participants', blank= True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) # Time remains the same after the first time its updated.

    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.name
    


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # one user has multiple Messages, User class is parent.
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # one room has multiple Messages, 
                                                             # room table is the pareent and Messages table is the children
    body = models.TextField()
    updated= models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]
