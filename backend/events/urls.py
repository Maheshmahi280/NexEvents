from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Events
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('events/bookmarks/', views.UserBookmarksView.as_view(), name='user-bookmarks'),
    path('events/create/', views.EventCreateView.as_view(), name='event-create'),
    path('events/my/', views.UserEventsView.as_view(), name='user-events'),
    path('events/<int:event_id>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<int:event_id>/delete/', views.EventDeleteView.as_view(), name='event-delete'),
    path('events/<int:event_id>/rsvp/', views.EventRSVPView.as_view(), name='event-rsvp'),
    path('events/<int:event_id>/book/', views.BookEventView.as_view(), name='event-book'),
    
    # User bookings and organizer revenue
    path('user/bookings/', views.UserBookingsView.as_view(), name='user-bookings'),
    path('organizer/revenue/', views.OrganizerRevenueView.as_view(), name='organizer-revenue'),
]
