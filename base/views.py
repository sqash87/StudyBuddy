from multiprocessing import context
from pydoc_data.topics import topics
from urllib.parse import uses_relative
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate,login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# passing dictionary (rooms) into the view functions.
# App templates go inside the app folders
# Project templates go inside the root folder. 


def loginPage(request):
    page = 'login'
    #if the user is already loged in, don't let them re-login
    if request.user.is_authenticated:
            return redirect ('home')
    
    if request.method == 'POST':
        email= request.POST.get('email')                  #getting from the frontend
        password= request.POST.get('password')                  #getting from the frontend
         
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exit.') 
    
    
        user = authenticate(request, email=email, password=password)
    
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'Username or password does not exist.')
   
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)                                            #using logout methood to sign out the user.
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()                            #creating a form
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)                  #pass in the user data and then get the form.
        if form.is_valid():                                    #Validating the credentials in the form
            user = form.save(commit=False)                     #get the user from the form.
            user.username = user.username.lower()              #lowercase the username that was created.
            user.save() 
            login(request, user)
            return redirect ('home') 
        else:
            messages.error(request, 'An Error Occured')


    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    # if the requested url 'q' is not empty
    q = request.GET.get('q') if request.GET.get('q') != None  else '' 
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | # url name contains any substring of topic name.
        Q(name__icontains=q) | 
        Q(description__icontains=q)
    )
    
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics':topics, 
    'room_count':room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

#this room function will call the room.html.
def room(request, pk):
    room = Room.objects.get(id=pk)                                
    room_messages = room.message_set.all()
    participants = room.participants.all()
    
    # This creates an object 'message' and inserts data into user, room, and body columns.
    if request.method == 'POST':
        message = Message.objects.create(
            user= request.user,
            room= room,
            body= request.POST.get('body')
        )
        room.participants.add(request.user)                                                #using room object to add an authenticated user in particpant column.
        return redirect('room', pk=room.id)
                                                                                              
    context = {'room': room, 'room_messages': room_messages, 'participants': participants} #passing vlaues as dictionary  
    return render(request, 'base/room.html', context)                                      # Rendering html file with the context dictionary.      

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() #getting rooms associated with the users.
    room_messages = user.message_set.all() # getting all the messages related to the user.
    topics = Topic.objects.all() #getting all the topics name from the Topic.
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)





#Restricting unauthoried users from creating a room and redirecting them to login page.
@login_required(login_url='/login')

def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST' :
        topic_name =request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name= request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')                   
    context = {'form': form, 'topics': topics}                          # form the key; it could be any room, form is the value
    return render(request, 'base/room_form.html', context)


#Restricting unauthoried users from update a room and redirecting them to login page.
@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)                    # getting room number id with the primary key
    form = RoomForm(instance=room)                    # This form will be oprefilled with the room value
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('User is not allowded here.')

    if request.method == 'POST':
        topic_name =request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name) 
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')                   #sending user back to he homepage.
    context = {'form': form, 'topics': topics, 'room':room}
    return render (request, 'base/room_form.html', context)


#Restricting unauthoried users from deleting a room and redirecting them to login page.
@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)                     #getting room number id with the primary key
    
    if request.user != room.host:
        return HttpResponse('User is not allowded here.')

    if request.method == 'POST':
         room.delete() #removing the item from the database.
         return redirect('home')

    return render (request, 'base/delete.html', {'obj': room}) # after deleting the room rednding the html tag.


@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)                     #getting room number id with the primary key
    
    if request.user != message.user:
        return HttpResponse('User is not allowded here.')

    if request.method == 'POST':
         message.delete() #removing the item from the database.
         return redirect('home')

    return render (request, 'base/delete.html', {'obj': message}) # after deleting the room rednding the html tag.


@login_required(login_url='/login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)


    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None  else '' 
    topics = Topic.objects.filter(name__icontains=q)
    return render (request, 'base/topics.html', {'topics':topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})