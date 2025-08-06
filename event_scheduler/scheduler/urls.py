from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

# DRF class-based views
from .views import (
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    AddSessionToEventAPIView,
    SessionListAPIView,
    SessionUpdateDeleteAPIView,
    OptimizedScheduleView
)

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'),

    # Web views
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),

    path('sessions/', views.session_list, name='session_list'),
    path('sessions/create/', views.session_create, name='session_create'),
    path('sessions/<int:pk>/edit/', views.session_update, name='session_update'),
    path('sessions/<int:pk>/delete/', views.session_delete, name='session_delete'),

    path('speakers/', views.speaker_list, name='speaker_list'),
    path('speakers/create/', views.speaker_create, name='speaker_create'),
    path('speakers/<int:pk>/edit/', views.speaker_update, name='speaker_update'),
    path('speakers/<int:pk>/delete/', views.speaker_delete, name='speaker_delete'),

    path('schedule/', views.schedule_view, name='schedule_view'),
    path('logout/', views.logout_view, name='logout'),



    # --------------------
    # ✅ API ENDPOINTS
    # --------------------

    # Event API
    path('api/events/', EventListCreateAPIView.as_view(), name='api_event_list'),
    path('api/events/<int:pk>/', EventRetrieveUpdateDestroyAPIView.as_view(), name='api_event_detail'),

    # Add Session to Event
    path('api/events/<int:pk>/sessions/', AddSessionToEventAPIView.as_view(), name='api_event_add_session'),

    # Session API
    path('api/sessions/', SessionListAPIView.as_view(), name='api_session_list'),
    path('api/sessions/<int:pk>/', SessionUpdateDeleteAPIView.as_view(), name='api_session_detail'),

    # Optimized Schedule API
    path('api/schedule/optimized/', OptimizedScheduleView.as_view(), name='api_optimized_schedule'),
]
