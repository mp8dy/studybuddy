from http.client import HTTPResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django import forms 
from django.contrib import messages

from .models import Profile, Course, StudySession, MessageTwo
from .forms import EditProfileForm, ProfileForm, SessionForm, MessageForm
from django.contrib.auth import logout


def home(request):
    return render(request, 'home.html')

def login(request):
    if request.user.is_authenticated and not (Profile.objects.filter(user_id=request.user.id)).exists():
        return HttpResponseRedirect(reverse('register'))
    return render(request, 'index.html')


def register(request):
    form = ProfileForm(request.POST) 
    if Profile.objects.filter(user_id=request.user.id).exists() and request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if (form.is_valid()):
        preferredName = request.POST['user']
        request.user.username = preferredName
        print(request.user.username)
        request.user.save()

        profile = form.save(commit=False)
        profile.user = request.user
        profile.save()

        return HttpResponseRedirect(reverse('addCourses'))
    
    context = {
        'form': form
    }
       
    return render(request, 'registerProfile.html', context)


def session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)

        if form.is_valid():
            new_session = StudySession()
            #session.users = request.user.objects.values_list('username', flat='True')
            new_session.save()
            #session.users.add(request.POST.get('users'))
            temp = request.POST.getlist('users')
            #session.m2mfield.add(*temp)
            new_session.users.add(*temp)
            #return HttpResponse(request.POST.items())
            new_session.date = request.POST.get('date')
            new_session.time = request.POST.get('time')
            new_session.location = request.POST.get('location')
            new_session.subject = request.POST.get('subject')
            new_session.save()
            service = build('calendar', 'v3', credentials=creds)

            event = {
                'summary': request.POST.get('subject') + " Study Session",
                'location': request.POST.get('location'),
                'description': 'Let\'s work together on this class!',
                'start': {
                    'dateTime': '2015-05-28T09:00:00-07:00',
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': '2015-05-28T17:00:00-07:00',
                    'timeZone': 'America/New_York',
                },
                'recurrence': [
                    'RRULE:FREQ=DAILY;COUNT=2'
                ],
                'attendees': [
                    {'email': 'lpage@example.com'},
                    {'email': 'sbrin@example.com'},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            event = service.events().insert(calendarId='primary', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))
            return HttpResponseRedirect(reverse('my_sessions'))

    else:
        form = SessionForm()

    return render(request, 'newSession.html', {'form': form})

def my_sessions(request):
    sessions = StudySession.objects.filter().all()
    sessions_dict = {
        'sessions': sessions
    }
    return render(request, 'sessions.html', sessions_dict)

def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)

        if form.is_valid():
            new_message = MessageTwo()
            new_message.sent_by = request.user.username
            new_message.save()
            temp = request.POST.getlist('to')
            new_message.to.add(*temp)
            new_message.message = request.POST.get('message')
            new_message.save()
            return HttpResponseRedirect(reverse('my_messages'))

    else:
        form = MessageForm()

    return render(request, 'newMessage.html', {'form': form})

def my_messages(request):
    messages = MessageTwo.objects.filter().all()
    messages_dict = {
        'messages': messages
    }
    return render(request, 'messages.html', messages_dict)

def profile(request):
    if not request.user.is_authenticated or not (Profile.objects.filter(user_id=request.user.id)).exists():
        return HttpResponseRedirect(reverse('login'))

    theUser = Profile.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        return HttpResponseRedirect(reverse('editProfile'))

    return render(request, 'profile.html', {"user" : theUser})

def calendar(request):
    return render(request, 'calendar.html')

def addCourses(request):
    if not request.user.is_authenticated or not (Profile.objects.filter(user_id=request.user.id)).exists():
        return HttpResponseRedirect(reverse('login'))
        
    allCourses = Course.objects.all() 
    theUser = Profile.objects.get(user_id=request.user.id)
    courseValid = True
    addedSuccess = False
    dupCourse = False

    if request.method == 'POST':
        if 'Filter' in request.POST:
            if Course.objects.filter(courseAbbv=request.POST['courseAb']).exists(): 
                allCourses = Course.objects.filter(courseAbbv=request.POST['courseAb'])

        if 'Add Course' in request.POST:    
            if (Course.objects.filter(courseAbbv=request.POST['courseAb']).exists() and Course.objects.filter(courseNumber=request.POST['courseNumb']).exists()): 
                if not theUser.courses.filter(courseAbbv=request.POST['courseAb'], courseNumber=request.POST['courseNumb']).exists():
                    theUser.courses.add(Course.objects.get(courseAbbv=request.POST['courseAb'], courseNumber=request.POST['courseNumb']))
                else:
                    dupCourse = True
                courseValid = True
                addedSuccess = True
            else:
                courseValid = False
                addedSuccess - False
                dupCourse = False
        
        if 'Reset Search' in request.POST:
            allCourses = Course.objects.all() 
            
        print('in post expression')
    else:
        allCourses = Course.objects.all()
    
    context = {
        'allCourses' : allCourses,
        'courseValid' : courseValid,
        'addedSuccess' : addedSuccess,
        'dupCourse' : dupCourse
    }
    
    return render(request, 'addCourses.html', context)

def logOut(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    logout(request)
    
    return render(request, 'index.html')

def findBuddies(request):
    allProfiles = Profile.objects.all()

    if request.method == 'POST':
        if 'Reset Search' in request.POST:
            allProfiles = Profile.objects.all()
        
        if 'Find Buddy' in request.POST:
            filteredProfiles = []
            foundBoth = False 

            for each in allProfiles:
                if each.courses.filter(courseAbbv=request.POST['courseAb'], courseNumber=request.POST['courseNumb']).exists():
                    filteredProfiles.append(each)
                    print(each.user)
                    foundBoth = True
                    continue 
                else: 
                    print("went through else")
                    if each.courses.filter(courseAbbv=request.POST['courseAb']).exists() and not foundBoth:
                        filteredProfiles.append(each)
                    if each.courses.filter(courseNumber=request.POST['courseNumb']).exists() and not foundBoth:
                        filteredProfiles.append(each)

            allProfiles = filteredProfiles

    else:
        allProfiles = Profile.objects.all()
    
    context = {
        'allProfiles' : allProfiles
    }
    return render(request, 'findBuddies.html', context)

def editProfile(request):
    form = EditProfileForm(request.POST)
    if request.method == 'POST':
        editedProfile = Profile.objects.get(user_id=request.user.id)
        if form.is_valid():
            editedProfile.about = form.cleaned_data['about']
            editedProfile.major = form.cleaned_data['major']
            editedProfile.save()
            return HttpResponseRedirect(reverse('profile'))
   
    context = {
        'form': form
    }
    return render(request, 'editProfile.html', context)