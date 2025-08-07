

from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Session
from .forms import EventForm
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

from rest_framework import generics, status
from rest_framework.response import Response
from .models import Event, Session, Speaker
from .serializers import EventSerializer, SessionSerializer, SpeakerSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.contrib.auth.decorators import login_required


from django.contrib.auth import logout

@csrf_exempt
def api_event_list(request):
    if request.method == 'GET':
        events = Event.objects.all().values('id', 'title', 'description', 'date', 'location')
        return JsonResponse(list(events), safe=False)

    if request.method == 'POST':
        data = json.loads(request.body)
        event = Event.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            date=data['date'],
            location=data['location']
        )
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': str(event.date),
            'location': event.location,
        })
    
@csrf_exempt
def api_event_detail(request, pk):
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

    if request.method == 'GET':
        sessions = event.sessions.select_related('speaker').all()
        session_list = [
            {
                'id': s.id,
                'title': s.title,
                'start_time': s.start_time.strftime('%H:%M'),
                'end_time': s.end_time.strftime('%H:%M'),
                'speaker': {
                    'id': s.speaker.id,
                    'name': s.speaker.name
                }
            }
            for s in sessions
        ]
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': str(event.date),
            'location': event.location,
            'sessions': session_list
        })

    elif request.method == 'PUT':
        data = json.loads(request.body)
        event.title = data.get('title', event.title)
        event.descript



# /events/ (GET, POST)
class EventListCreateAPIView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

# /events/<id>/ (GET, PUT, DELETE)
class EventRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

# /events/<id>/sessions/ (POST)
class AddSessionToEventAPIView(APIView):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        data = request.data.copy()
        data['event'] = event.id
        serializer = SessionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# /sessions/ (GET)
class SessionListAPIView(generics.ListAPIView):
    queryset = Session.objects.select_related('speaker', 'event').all()
    serializer_class = SessionSerializer

# /sessions/<id>/ (PUT, DELETE)
class SessionUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

# /events/optimized/ (GET)
class OptimizedScheduleView(APIView):
    def get(self, request):
        events = Event.objects.prefetch_related('sessions__speaker')
        result = []
        for event in events:
            sessions_data = []
            for session in event.sessions.all():
                sessions_data.append({
                    'title': session.title,
                    'start_time': session.start_time,
                    'end_time': session.end_time,
                    'speaker': session.speaker.name
                })
            result.append({
                'event': event.title,
                'sessions': sessions_data
            })
        return Response(result)


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('event_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def event_list(request):
    events = Event.objects.filter(created_by=request.user)
    return render(request, 'scheduler/event_list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    sessions = Session.objects.filter(event=event)
    return render(request, 'scheduler/event_detail.html', {'event': event, 'sessions': sessions})

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # ✅ link to logged-in user
            event.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'scheduler/event_form.html', {'form': form})


@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'scheduler/event_form.html', {'form': form})

@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'scheduler/event_confirm_delete.html', {'event': event})

from .models import Session
from .forms import SessionForm

def session_list(request):
    sessions = Session.objects.select_related('event', 'speaker').all()
    return render(request, 'scheduler/session_list.html', {'sessions': sessions})

def session_create(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            try:
                session = form.save(commit=False)
                session.clean()  # manually call your validation
                session.save()
                return redirect('session_list')
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = SessionForm()
    return render(request, 'scheduler/session_form.html', {'form': form})


@login_required
def session_update(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            try:
                session = form.save(commit=False)
                session.clean()
                session.save()
                return redirect('session_list')
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = SessionForm(instance=session)
    return render(request, 'scheduler/session_form.html', {'form': form})

@login_required
def session_delete(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        session.delete()
        return redirect('session_list')
    return render(request, 'scheduler/session_confirm_delete.html', {'session': session})

from .models import Speaker
from .forms import SpeakerForm

def speaker_list(request):
    speakers = Speaker.objects.all()
    return render(request, 'scheduler/speaker_list.html', {'speakers': speakers})

def speaker_create(request):
    if request.method == 'POST':
        form = SpeakerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('speaker_list')
    else:
        form = SpeakerForm()
    return render(request, 'scheduler/speaker_form.html', {'form': form})

@login_required
def speaker_update(request, pk):
    speaker = get_object_or_404(Speaker, pk=pk)
    if request.method == 'POST':
        form = SpeakerForm(request.POST, instance=speaker)
        if form.is_valid():
            form.save()
            return redirect('speaker_list')
    else:
        form = SpeakerForm(instance=speaker)
    return render(request, 'scheduler/speaker_form.html', {'form': form})

@login_required
def speaker_delete(request, pk):
    speaker = get_object_or_404(Speaker, pk=pk)
    if request.method == 'POST':
        speaker.delete()
        return redirect('speaker_list')
    return render(request, 'scheduler/speaker_confirm_delete.html', {'speaker': speaker})

from django.core.exceptions import ValidationError

def clean(self):
    # Skip validation if any required field is missing
    if not all([self.event, self.speaker, self.start_time, self.end_time]):
        return

    # 1. Prevent overlapping sessions within the same event
    overlapping = Session.objects.filter(
        event=self.event,
        start_time__lt=self.end_time,
        end_time__gt=self.start_time
    ).exclude(pk=self.pk)

    if overlapping.exists():
        raise ValidationError("This session overlaps with another session in the same event.")

    # 2. Prevent speaker double-booking
    conflict = Session.objects.filter(
        speaker=self.speaker,
        start_time__lt=self.end_time,
        end_time__gt=self.start_time
    ).exclude(pk=self.pk)

    if conflict.exists():
        raise ValidationError("This speaker is already scheduled in another session at this time.")
    
def schedule_view(request):
    events = Event.objects.prefetch_related('sessions').order_by('date')
    return render(request, 'scheduler/schedule.html', {'events': events})


def logout_view(request):
    logout(request)
    return redirect('home')