from django.urls import path
from . import views
from .views import MyTokenObtainPairView

urlpatterns = [
    # Auth
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Events
    path('events/', views.events_list_create, name='events_list_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),

    # Bookings
    path('bookings/', views.create_booking, name='create_booking'),
    path('bookings/my/', views.my_bookings, name='my_bookings'),
]
