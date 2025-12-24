from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, Alert

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'date_joined', 'password'
        ]
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user with password handling"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""

    class Meta:
        model = Event
        fields = [
            'id', 'source_name', 'event_type', 'severity',
            'description', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

    def validate_severity(self, value):
        """Validate severity choices"""
        valid_severities = [choice[0] for choice in Event.SEVERITY_CHOICES]
        if value not in valid_severities:
            raise serializers.ValidationError(
                f"Severity must be one of: {', '.join(valid_severities)}"
            )
        return value

    def validate_source_name(self, value):
        """Validate source name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Source name cannot be empty")
        return value.strip()

    def validate_event_type(self, value):
        """Validate event type is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Event type cannot be empty")
        return value.strip()


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""
    event = EventSerializer(read_only=True)
    event_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'event', 'event_id', 'status', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'created_at', 'resolved_at']

    def validate_status(self, value):
        """Validate status choices"""
        valid_statuses = [choice[0] for choice in Alert.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value


class AlertStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating alert status only"""

    class Meta:
        model = Alert
        fields = ['status']
        read_only_fields = ['id', 'event', 'created_at', 'resolved_at']

    def validate_status(self, value):
        """Validate status choices"""
        valid_statuses = [choice[0] for choice in Alert.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value
