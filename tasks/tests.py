from pytz import timezone
from tasks.tasks import send_periodic_email
from tasks.views import GenericTaskCreateView, GenericTaskView
from .models import *
from django.core import mail
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
# Create your tests here.


class TaskModelTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman")

    def test_unauthenticated(self):
        """
        Test that an unauthenticated user cannot access the task list
        """
        response = self.client.get("/tasks")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/tasks")

    def test_authenticated(self):
        """
        Test that an authenticated user can access the task list
        """
        request = self.factory.get("/tasks")
        request.user = self.user
        response = GenericTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_create_task(self):
        """
        Test the create task function
        """
        request = self.factory.post(
            "/create-tasks", {"title": "Demo Task", "description": "Something", "priority": 10, "status": "PENDING"})
        request.user = self.user
        response = GenericTaskCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/tasks")
        self.assertEqual(Task.objects.filter(
            title="Demo Task", priority=10).count(), 1)

    def test_report_mail(self):
        """
        Test mails
        """
        user = User.objects.create(
            username="demo", password="demo@123", email="demo@demo.com"
        )
        user.save()
        report = Reports.objects.create(timing="00:00", user=user)
        report.save()
        send_periodic_email()
        self.assertEqual(len(mail.outbox), 1)
