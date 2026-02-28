from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    organiser = serializers.StringRelatedField(read_only=True)
    organiser_username = serializers.CharField(source='organiser.username', read_only=True)
    organiser_name = serializers.CharField(source='organiser.get_full_name', read_only=True)
    interested_count = serializers.SerializerMethodField()

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
            'created_at',
        ]
        read_only_fields = ['organiser', 'created_at', 'id']

    def get_interested_count(self, obj):
        # Return 0 if interested_users doesn't exist, otherwise return count
        if hasattr(obj, 'interested_users'):
            return obj.interested_users.count()
        return 0
