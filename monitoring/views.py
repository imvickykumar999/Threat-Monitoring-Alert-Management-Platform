from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, ChoiceFilter
from rest_framework.filters import OrderingFilter
from django.contrib.auth import get_user_model

from .models import Event, Alert
from .serializers import (
    UserSerializer, EventSerializer, AlertSerializer,
    AlertStatusUpdateSerializer
)
from .permissions import IsAdminUser, IsAnalystOrAdmin, IsAdminOrReadOnly

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User management"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Only admins can manage users

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class EventFilter(FilterSet):
    """Filter for Event model"""
    severity = ChoiceFilter(choices=Event.SEVERITY_CHOICES)
    event_type = ChoiceFilter(field_name='event_type', lookup_expr='icontains')

    class Meta:
        model = Event
        fields = ['severity', 'event_type', 'source_name']


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for Event management"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]  # Admins can create/edit, analysts can read
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EventFilter
    ordering_fields = ['timestamp', 'severity', 'source_name']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Optimize queries by selecting related fields"""
        return self.queryset.select_related()


class AlertFilter(FilterSet):
    """Filter for Alert model"""
    status = ChoiceFilter(choices=Alert.STATUS_CHOICES)
    severity = ChoiceFilter(field_name='event__severity', choices=Event.SEVERITY_CHOICES)

    class Meta:
        model = Alert
        fields = ['status', 'severity']


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet for Alert management"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAnalystOrAdmin]  # Analysts can read, admins can modify
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AlertFilter
    ordering_fields = ['created_at', 'status', 'event__severity']
    ordering = ['-created_at']

    def get_queryset(self):
        """Optimize queries by selecting related event data"""
        return self.queryset.select_related('event')

    def get_serializer_class(self):
        """Use different serializer for partial updates"""
        if self.action == 'partial_update':
            return AlertStatusUpdateSerializer
        return AlertSerializer

    def update(self, request, *args, **kwargs):
        """Custom update method with permission check"""
        instance = self.get_object()

        # Check if user is admin for status updates
        if 'status' in request.data and not request.user.is_admin():
            return Response(
                {"error": "Only administrators can update alert status"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Custom partial update method with permission check"""
        instance = self.get_object()

        # Check if user is admin for status updates
        if 'status' in request.data and not request.user.is_admin():
            return Response(
                {"error": "Only administrators can update alert status"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request, *args, **kwargs)