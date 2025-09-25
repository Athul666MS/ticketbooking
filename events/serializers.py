from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, Booking

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = 'user'
        user.save()
        return user

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        total = data.get('total_seats', None)
        available = data.get('available_seats', None)
        if total is not None and available is not None and available > total:
            raise serializers.ValidationError('available_seats cannot be greater than total_seats')
        return data

class BookingSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ('id', 'user', 'event', 'seats_booked', 'status', 'booked_at')
        read_only_fields = ('id', 'user', 'status', 'booked_at')

class BookingCreateSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    seats = serializers.IntegerField(min_value=1)

    def validate_event_id(self, value):
        try:
            Event.objects.get(pk=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError('Event not found')
        return value
