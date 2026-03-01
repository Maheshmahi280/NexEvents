from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, Booking


class EventSerializer(serializers.ModelSerializer):
    organiser = serializers.StringRelatedField(read_only=True)
    organiser_username = serializers.CharField(source='organiser.username', read_only=True)
    organiser_name = serializers.CharField(source='organiser.get_full_name', read_only=True)
    interested_count = serializers.SerializerMethodField()
    booking_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    is_booked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'description',
            'date_time',
            'location',
            'category',
            'cover_image',
            'ticket_price',
            'organiser',
            'organiser_username',
            'organiser_name',
            'interested_count',
            'booking_count',
            'total_revenue',
            'is_booked_by_user',
            'created_at',
        ]
        read_only_fields = ['organiser', 'created_at', 'id']

    def get_interested_count(self, obj):
        # Return 0 if interested_users doesn't exist, otherwise return count
        if hasattr(obj, 'interested_users'):
            return obj.interested_users.count()
        return 0

    def get_booking_count(self, obj):
        """Get number of confirmed bookings"""
        return obj.get_booking_count()

    def get_total_revenue(self, obj):
        """Get total revenue from bookings"""
        return str(obj.get_total_revenue())

    def get_is_booked_by_user(self, obj):
        """Check if current user has booked this event"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Booking.objects.filter(
                event=obj,
                attendee=request.user,
                status='confirmed'
            ).exists()
        return False


class BookingSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    attendee_name = serializers.CharField(source='attendee.get_full_name', read_only=True)
    organiser_name = serializers.CharField(source='event.organiser.get_full_name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'event',
            'event_name',
            'attendee',
            'attendee_name',
            'organiser_name',
            'amount',
            'status',
            'booking_date',
        ]
        read_only_fields = ['id', 'booking_date', 'amount']
