from email.policy import default
from pyexpat import model
from telnetlib import Telnet
from venv import create
from django.db import models
from django.contrib.auth.models import AbstractUser




#User Model
class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique= True, null=True)
    bio = models.TextField(null= True)

    avatar = models.ImageField(null= True, default="avatar.svg")

  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


#Topic Model
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

#Room Model: 
# By includimg user and topic columns in the room table,
# I will have access to all the columns of the user and Topic tables. 
class Room(models.Model):
    
    #One user has many rooms but one room must belong to only one user
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null= True)
    
    #one topic has many rooms but one room must belong to only one topic      
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null= True)     
    
    name = models.CharField(max_length=200)
    
    description = models.TextField(null= True, blank=True)
    participants= models.ManyToManyField(User, related_name = 'participants', blank= True)
    updated = models.DateTimeField(auto_now=True)
    # Time remains the same after the first time its updated.
    created = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.name
    

#Message Model: 
# user | room | body |
# user(user) has messaged in a certain room(room) with contents(body)
class Message(models.Model):
    #one user has multiple Messages, User class is parent.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #one room has multiple Messages,  
    #room table is the pareent and Messages table is the children
    room = models.ForeignKey(Room, on_delete=models.CASCADE) 
                                                             
    body = models.TextField()
    updated= models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]
