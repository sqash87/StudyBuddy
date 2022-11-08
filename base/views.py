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
        #getting email from the frontend 
        email= request.POST.get('email')  
        #getting dpassword from the frontend                 
        password= request.POST.get('password')            
         
        #getting the user with the email
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exit.') 
        
        # authenticate() should check the credentials it gets and return a user object
        # that matches those credentials if the credentials are valid.  

        user = authenticate(request, email=email, password=password)
    
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'Username or password does not exist.')
    
    context = {'page': page}
    #rendering(send it back to the html page.) the "login_register.html" page with context
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)                                            #using logout methood to sign out the user.
    return redirect('home')


def registerPage(request):
    #creating a form object 
    form = MyUserCreationForm()                            
    if request.method == 'POST':
        # "request.post" will contain the user data when they click the register button.
        #  Then creating a "form" object by passing the user data into the "MyUserCreationForm" class
        #  Now, form contains user name.
        form = MyUserCreationForm(request.POST)
        
        #Validating the credential of the user or the form               
        if form.is_valid():                                    
            user = form.save(commit=False) 
            #lowercase the username that was created.                    
            user.username = user.username.lower()            
         
            user.save() 
            login(request, user)
            return redirect ('home') 
        else:
            messages.error(request, 'An Error Occured')

    return render(request, 'base/login_register.html', {'form': form})


#These functions here render the data out inside the html template.

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
    #Getting a particlular key with the primary key,
    room = Room.objects.get(id=pk) 
    #getting the messages in that room.                               
    room_messages = room.message_set.all()
    #getting all the participants of that room.
    participants = room.participants.all()
    
    # This creates an object 'message' and inserts data into user, room, and body columns.
    if request.method == 'POST':
        message = Message.objects.create(
            user= request.user,
            room= room,
            body= request.POST.get('body')
        )
        #using room object to add an authenticated user in particpant column.
        room.participants.add(request.user)                                                
        return redirect('room', pk=room.id)

    #passing vlaues as dictionary 
    #Rendering html file with the context dictionary.                                                                                              
    context = {'room': room, 'room_messages': room_messages, 'participants': participants} 
    return render(request, 'base/room.html', context)                                      


def userProfile(request, pk):
    #getting the user with the primary key.
    user = User.objects.get(id=pk)
    #since user column was added into the room table, I can access the rooms created by any particular user.
    rooms = user.room_set.all()
    #since user column was added into the message table, I can get meaages of a particular user
    room_messages = user.message_set.all() 
    topics = Topic.objects.all() 
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    
    #rendering the /profile.html with the context dictionary.
    return render(request, 'base/profile.html', context)





#Restricting unauthoried users from creating a room and redirecting them to login page.
@login_required(login_url='/login')

def createRoom(request):
    
    # "RoomForm" is a class that has all the data fields of Room Model.
    # "from" is an object in this function which will be passed as context dictionary
    # into the "room_form.html" when renderimg it and thefore, "room_form.html" page will have
    # access to this form. Input data from the user can be straight written into the Room model 
    # using this form. 
    
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST' :
        
        #using request method to get the name of the topic from the user input.
        topic_name =request.POST.get('topic')
        
        #creating a row contains topic name in the topic model
        topic,created = Topic.objects.get_or_create(name=topic_name)
        
        # creating data into the 4 columns of Room Model.
        Room.objects.create(
            
            host=request.user,
            topic=topic,
            # 'name' keyword has to be the same as the one inside "room_form.html"
            name= request.POST.get('name'),

            description = request.POST.get('description')
        )
        return redirect('home')                   
    context = {'form': form, 'topics': topics}                          # form the key; it could be any room, form is the value
    return render(request, 'base/room_form.html', context)


#Restricting unauthoried users from update a room and redirecting them to login page.
@login_required(login_url='/login')
def updateRoom(request, pk):
    #getting room number with id that we are gonna update.
    room = Room.objects.get(id=pk) 
    # "instance" prefills the form with the existig data.                
    form = RoomForm(instance=room)                    
    topics = Topic.objects.all()
    
    #Only the creator of the room can edit the room.
    if request.user != room.host:
        return HttpResponse('User is not allowded here.')
    
    # 2: When the "form" inside the "room_form.html" sends back the inputted data 
    #    into the same page which is "room_form.html", 
    #    "if request.method == 'POST'": section of codes get activated 
    #    and rteurn back to the homepage.
    if request.method == 'POST':
        topic_name =request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name) 
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')                   #sending user back to he homepage.
    
    context = {'form': form, 'topics': topics, 'room':room}
    # 1: Render the "room_form.html" with the prefilled data "form" from the room model 
    #    and then if request.method == 'POST': section of code gets activated when "form" inside the 
    #    "room_form.html" sends the inptted data back to the same page. 
    return render (request, 'base/room_form.html', context)


#Restricting unauthoried users from deleting a room and redirecting them to login page.
@login_required(login_url='/login')
def deleteRoom(request, pk):
    
    #getting room number id with the primary key
    room = Room.objects.get(id=pk)                    
    
    #only the author of the room can delete the room.
    if request.user != room.host:
        return HttpResponse('User is not allowded here.')

    #if the user confirm the "delete" button, this part of the code will be invoked.
    if request.method == 'POST':
         room.delete() 
         return redirect('home')
    #initially, deleteRoom() will render the "delete.html" 
    return render (request, 'base/delete.html', {'obj': room}) 


@login_required(login_url='/login')
def deleteMessage(request, pk):
   
    message = Message.objects.get(id=pk)                     
    #only the auther of the "text" can delete his or her text 
    if request.user != message.user:
        return HttpResponse('User is not allowded here.')

    #if the user hit "delete" this section of the code will be invoked.
    if request.method == 'POST':
         #removing the item from the database.
         message.delete() 
         return redirect('home')
    
    #initially, deleteMessage() will render the "delete.html" 
    return render (request, 'base/delete.html', {'obj': message}) 


#user has to be logged in for this function to be invoked.
@login_required(login_url='/login')
def updateUser(request):
    user = request.user
    #prefilled the "form" with the user's existing data from the user model.
    form = UserForm(instance=user)
    
   
    # if < Form > tag sends a request using "post" method,
    # This section will be invoked in case user decides to chnage anything. 
    if request.method == 'POST':
        #creating a new form with the request data
        form = UserForm(request.POST, request.FILES, instance=user)
        #validating the form
        if form.is_valid():
            form.save()
            #redirect the page to the user-profile.
            return redirect('user-profile', pk=user.id)

    # render the "update-user.html" first with the form.
    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None  else '' 
    topics = Topic.objects.filter(name__icontains=q)
    return render (request, 'base/topics.html', {'topics':topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
