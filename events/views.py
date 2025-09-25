from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserRegisterSerializer, EventSerializer, BookingSerializer, BookingCreateSerializer
)
from .models import Event, Booking
from django.contrib.auth import get_user_model
from .permissions import IsAdminRole

User = get_user_model()

# Use Simple JWT's token view for login
class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """POST /api/auth/signup/"""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def events_list_create(request):
    """
    GET /api/events/ -> public list
    POST /api/events/ -> admin only create
    """
    if request.method == 'GET':
        events = Event.objects.all().order_by('date')
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    # POST -> require admin role
    if request.method == 'POST':
        if not request.user or not request.user.is_authenticated or request.user.role != 'admin':
            return Response({'detail': 'Admin privileges required'}, status=status.HTTP_403_FORBIDDEN)
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def event_detail(request, pk):

    event = get_object_or_404(Event, pk=pk)
    if request.method == 'GET':
        serializer = EventSerializer(event)
        return Response(serializer.data)

    if not request.user or not request.user.is_authenticated or request.user.role != 'admin':
        return Response({'detail': 'Admin privileges required'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    """
    POST /api/bookings/  body: {"event_id": 1, "seats": 2}
    Uses transaction + select_for_update to prevent overbooking.
    """
    serializer = BookingCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    event_id = serializer.validated_data['event_id']
    seats = serializer.validated_data['seats']

    try:
        with transaction.atomic():
            event = Event.objects.select_for_update().get(pk=event_id)
            if event.available_seats < seats:
                return Response({'detail': 'Not enough seats available'}, status=status.HTTP_400_BAD_REQUEST)
            event.available_seats -= seats
            event.save()
            booking = Booking.objects.create(user=request.user, event=event, seats_booked=seats)
            booking_serializer = BookingSerializer(booking)
            return Response(booking_serializer.data, status=status.HTTP_201_CREATED)
    except Event.DoesNotExist:
        return Response({'detail': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'detail': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    """GET /api/bookings/my/ -> current user's bookings"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)
