"""
URL configuration for backend project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from events import views as event_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/', include('events.urls')),
    path('api/logout/', event_views.logout_user, name='api_logout'),
    path('api/user/profile/', event_views.user_profile, name='api_user_profile'),
    
    # Template/Page routes
    path('', event_views.index, name='home'),
    path('join', event_views.join_page, name='join-page'),
    path('join/attending', event_views.attending_join, name='attending-join'),
    path('join/organizing', event_views.organizing_join, name='organizing-join'),
    path('login', event_views.login_page, name='login-page'),
    path('register', event_views.register_page, name='register-page'),
    path('dashboard', event_views.dashboard_page, name='dashboard-page'),
    path('seeker-dashboard', event_views.seeker_dashboard, name='seeker-dashboard'),
    path('organizer-dashboard', event_views.organizer_dashboard, name='organizer-dashboard'),
    path('create-event', event_views.create_event_page, name='create-event-page'),
    path('event/<int:event_id>', event_views.event_details_page, name='event-details-page'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')

