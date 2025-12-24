from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Event, Alert

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        self.analyst_user = User.objects.create_user(
            username='analyst',
            email='analyst@test.com',
            password='testpass123',
            role='analyst'
        )

    def test_user_roles(self):
        """Test user role methods"""
        self.assertTrue(self.admin_user.is_admin())
        self.assertFalse(self.admin_user.is_analyst())
        self.assertTrue(self.analyst_user.is_analyst())
        self.assertFalse(self.analyst_user.is_admin())


class EventModelTest(TestCase):
    """Test cases for Event model and auto-alert creation"""

    def test_event_creation_low_severity(self):
        """Test that Low severity events don't create alerts"""
        event = Event.objects.create(
            source_name='Test Source',
            event_type='test_event',
            severity='Low',
            description='Test low severity event'
        )

        # Check that no alert was created
        self.assertEqual(Alert.objects.count(), 0)
        self.assertFalse(event.should_create_alert())

    def test_event_creation_medium_severity(self):
        """Test that Medium severity events don't create alerts"""
        event = Event.objects.create(
            source_name='Test Source',
            event_type='test_event',
            severity='Medium',
            description='Test medium severity event'
        )

        # Check that no alert was created
        self.assertEqual(Alert.objects.count(), 0)
        self.assertFalse(event.should_create_alert())

    def test_event_creation_high_severity(self):
        """Test that High severity events create alerts automatically"""
        event = Event.objects.create(
            source_name='Test Source',
            event_type='intrusion',
            severity='High',
            description='Test high severity event'
        )

        # Check that alert was created
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.event, event)
        self.assertEqual(alert.status, 'Open')
        self.assertTrue(event.should_create_alert())

    def test_event_creation_critical_severity(self):
        """Test that Critical severity events create alerts automatically"""
        event = Event.objects.create(
            source_name='Test Source',
            event_type='malware',
            severity='Critical',
            description='Test critical severity event'
        )

        # Check that alert was created
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.event, event)
        self.assertEqual(alert.status, 'Open')
        self.assertTrue(event.should_create_alert())

    def test_multiple_high_severity_events(self):
        """Test that multiple high severity events create separate alerts"""
        event1 = Event.objects.create(
            source_name='Source 1',
            event_type='intrusion',
            severity='High',
            description='First high severity event'
        )
        event2 = Event.objects.create(
            source_name='Source 2',
            event_type='anomaly',
            severity='Critical',
            description='Second high severity event'
        )

        # Check that two alerts were created
        self.assertEqual(Alert.objects.count(), 2)
        alerts = Alert.objects.order_by('created_at')  # Order by creation time ascending
        self.assertEqual(alerts[0].event, event1)
        self.assertEqual(alerts[1].event, event2)


class AlertModelTest(TestCase):
    """Test cases for Alert model"""

    def setUp(self):
        self.event = Event.objects.create(
            source_name='Test Source',
            event_type='test_event',
            severity='High',
            description='Test event for alert'
        )
        self.alert = Alert.objects.first()

    def test_alert_status_update_resolved(self):
        """Test that resolving an alert sets resolved_at timestamp"""
        self.assertIsNone(self.alert.resolved_at)

        self.alert.status = 'Resolved'
        self.alert.save()

        self.alert.refresh_from_db()
        self.assertIsNotNone(self.alert.resolved_at)

    def test_alert_status_update_acknowledged(self):
        """Test that acknowledging an alert doesn't set resolved_at"""
        self.alert.status = 'Acknowledged'
        self.alert.save()

        self.alert.refresh_from_db()
        self.assertIsNone(self.alert.resolved_at)


class EventAPITest(APITestCase):
    """Test cases for Event API endpoints"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        self.analyst_user = User.objects.create_user(
            username='analyst',
            email='analyst@test.com',
            password='testpass123',
            role='analyst'
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_create_event_as_admin(self):
        """Test creating an event as admin"""
        data = {
            'source_name': 'API Test Source',
            'event_type': 'api_test',
            'severity': 'High',
            'description': 'Test event created via API'
        }

        response = self.client.post(reverse('event-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that event and alert were created
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Alert.objects.count(), 1)

    def test_create_event_invalid_severity(self):
        """Test creating an event with invalid severity"""
        data = {
            'source_name': 'API Test Source',
            'event_type': 'api_test',
            'severity': 'Invalid',
            'description': 'Test event with invalid severity'
        }

        response = self.client.post(reverse('event-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_events_with_filtering(self):
        """Test listing events with severity filtering"""
        # Create test events
        Event.objects.create(source_name='Source1', event_type='type1', severity='Low', description='Low event')
        Event.objects.create(source_name='Source2', event_type='type2', severity='High', description='High event')

        response = self.client.get(reverse('event-list'), {'severity': 'High'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['severity'], 'High')


class AlertAPITest(APITestCase):
    """Test cases for Alert API endpoints"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        self.analyst_user = User.objects.create_user(
            username='analyst',
            email='analyst@test.com',
            password='testpass123',
            role='analyst'
        )

        # Create an event that triggers an alert
        self.event = Event.objects.create(
            source_name='Test Source',
            event_type='test_event',
            severity='High',
            description='Test event'
        )
        self.alert = Alert.objects.first()

    def test_analyst_can_read_alerts(self):
        """Test that analysts can read alerts"""
        self.client.force_authenticate(user=self.analyst_user)

        response = self.client.get(reverse('alert-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_analyst_cannot_update_alert_status(self):
        """Test that analysts cannot update alert status"""
        self.client.force_authenticate(user=self.analyst_user)

        data = {'status': 'Resolved'}
        response = self.client.patch(reverse('alert-detail', kwargs={'pk': self.alert.id}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_alert_status(self):
        """Test that admins can update alert status"""
        self.client.force_authenticate(user=self.admin_user)

        data = {'status': 'Resolved'}
        response = self.client.patch(reverse('alert-detail', kwargs={'pk': self.alert.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that alert was updated
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, 'Resolved')
        self.assertIsNotNone(self.alert.resolved_at)

    def test_list_alerts_with_filtering(self):
        """Test listing alerts with status filtering"""
        # Create another alert
        event2 = Event.objects.create(
            source_name='Source2',
            event_type='type2',
            severity='Critical',
            description='Critical event'
        )
        alert2 = Alert.objects.get(event=event2)

        # Update first alert to resolved
        self.alert.status = 'Resolved'
        self.alert.save()

        self.client.force_authenticate(user=self.admin_user)

        # Filter by Open status
        response = self.client.get(reverse('alert-list'), {'status': 'Open'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'Open')

        # Filter by Resolved status
        response = self.client.get(reverse('alert-list'), {'status': 'Resolved'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'Resolved')