from django.contrib.auth.models import User
from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           ChoiceFilter, DjangoFilterBackend, DateFromToRangeFilter,
                                           FilterSet)
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from tasks.models import STATUS_CHOICES, Task, TaskHistory


#  TASK API
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        user = UserSerializer(read_only=True)
        fields = ["title", "description", "user", "completed", "status"]


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    completed = BooleanFilter()
    status = ChoiceFilter(choices=STATUS_CHOICES)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_class = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        task = self.get_object()
        new_status = serializer.validated_data.get("status")
        print(task.status, new_status)
        if new_status != task.status:
            TaskHistory.objects.create(
                task=task, old_status=task.status, new_status=new_status, user=self.request.user)
        serializer.save(user=self.request.user)


# TASK HISTORY

class TaskHistorySerializer(ModelSerializer):

    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskHistory
        fields = ["old_status", "new_status", "updated_date", "task"]


class TaskHistoryFilter(FilterSet):
    updated_date = DateFromToRangeFilter()
    new_status = ChoiceFilter(choices=STATUS_CHOICES)


class TaskHistoryViewSet(ModelViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer

    permission_class = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskHistoryFilter

    def get_queryset(self):
        return TaskHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
