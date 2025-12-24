from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Event, Alert


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin for Event model"""
    list_display = ('source_name', 'event_type', 'severity', 'timestamp')
    list_filter = ('severity', 'event_type', 'source_name', 'timestamp')
    search_fields = ('source_name', 'event_type', 'description')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Event Information', {
            'fields': ('source_name', 'event_type', 'severity', 'description')
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin for Alert model"""
    list_display = ('id', 'event', 'status', 'created_at', 'resolved_at')
    list_filter = ('status', 'created_at', 'resolved_at')
    search_fields = ('event__source_name', 'event__event_type')
    readonly_fields = ('created_at', 'resolved_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Alert Information', {
            'fields': ('event', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize admin queries"""
        return super().get_queryset(request).select_related('event')