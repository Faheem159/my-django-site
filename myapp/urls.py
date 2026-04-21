"""
URL configuration for mydjangosite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('portal/', views.tenant_portal, name='tenant_portal'),
    path('update/<int:pk>/', views.update_status, name='update_status'),
    path('profile/', views.profile, name='profile'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/delete/<int:pk>/', views.delete_announcement, name='delete_announcement'),
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:tenant_id>/', views.chat_detail, name='chat_detail'),
    path('messages/', views.tenant_chat, name='tenant_chat'),
]
