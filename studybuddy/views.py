from http.client import HTTPResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django import forms 
from django.contrib import messages
# import pytz
from django.utils import timezone

from .models import Profile, Course
from .models import StudySession
from .forms import ProfileForm
from .forms import SessionForm
from django.contrib.auth import logout

now = timezone.now()

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
    print("event")
    if request.method == 'POST':
        form = SessionForm(request.POST)

        if form.is_valid():
            session = StudySession()
            #session.users = request.user.objects.values_list('username', flat='True')
            session.save()
            #session.users.add(request.POST.get('users'))
            temp = request.POST.getlist('users')
            #session.m2mfield.add(*temp)
            session.users.add(*temp)
            #return HttpResponse(request.POST.items())
            session.date = request.POST.get('date')
            session.time = request.POST.get('time')
            session.location = request.POST.get('location')
            session.subject = request.POST.get('subject')
            session.save()
            return render(request, 'sessions.html', {'session': session})
    else:
        form = SessionForm()

    return render(request, 'newSession.html', {'form': form})

def event(request):
    print("event")
    if request.method == 'POST':
        form = SessionForm(request.POST)

        if form.is_valid():
            print(now)
            session = StudySession()
            list_users = request.POST.getlist('users')
            event = {
                'summary': request.POST.get('summary'),
                'location': request.POST.get('location'),
                'description': request.POST.get('description'),
                'start': {
                    'dateTime': request.POST.get('startTime'),
                    'timeZone': 'America/New_York', 
                },
                'end': {
                    'dateTime': request.POST.get('endTime'),
                    'timeZone': 'America/New_York', 
                },
                'attendees': [
                    {'email': list_users[0].email}
                ]
            }
            event = service.events().insert(calendar='c_8gg3c3rg0uee6rt83ajmm6c3v0@group.calendar.google.com', body=event).execute()
            print('Event created %s' % (event.get('htmlLink')))
    else:
        form = SessionForm()

    
    events.insert()
    # return render(request, 'newSession.html', {'form': form})


def profile(request):
    theUser = Profile.objects.get(user_id=request.user.id)
    return render(request, 'profile.html', {"user" : theUser})

def calendar(request):
    return render(request, 'calendar.html')

def addCourses(request):
    print("courses")
    allCourses = Course.objects.all() 
    theUser = Profile.objects.get(user_id=request.user.id)
    courseValid = True

    if request.method == 'POST':
        if 'Filter' in request.POST:
            if Course.objects.filter(courseAbbv=request.POST['courseAb']).exists(): 
                allCourses = Course.objects.filter(courseAbbv=request.POST['courseAb'])

        if 'Add Course' in request.POST:    
            if (Course.objects.filter(courseAbbv=request.POST['courseAb']).exists() and Course.objects.filter(courseNumber=request.POST['courseNumb']).exists()): 
                theUser.courses.add(Course.objects.get(courseAbbv=request.POST['courseAb'], courseNumber=request.POST['courseNumb']))
                print('course added to current user')
                courseValid = True
            else:
                courseValid = False
        
        if 'Reset Search' in request.POST:
            allCourses = Course.objects.all() 
            
        print('in post expression')
    else:
        allCourses = Course.objects.all()
    
    context = {
        'allCourses' : allCourses,
        'courseValid' : courseValid
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

