from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError

from django.shortcuts import redirect
from django.views import View
from django.views.generic.edit import CreateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.views.generic.list import ListView
from django import forms
from django.forms import ModelForm
from django.db.models import F

from tasks.models import Task


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return redirect("/tasks")


class AuthorizedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class TaskCreateForm(ModelForm):
    def clean_title(self):
        title = self.cleaned_data.get("title")
        if len(title) < 2:
            raise ValidationError("Title is too small")
        return title

    class Meta:
        model = Task
        fields = ["title", "description", "completed", "priority"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input mb-4", }),
            "description": forms.Textarea(attrs={"class": "input mb-4", "rows": "3"}),
            "completed": forms.CheckboxInput(attrs={"class": ""}),
            "priority": forms.NumberInput(attrs={"class": "input"}),
        }


class GenericTaskView(AuthorizedTaskManager, ListView):
    model = Task.objects.filter(deleted=False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginated_by = 5

    def get_queryset(self):
        status = self.request.GET.get("status")

        tasks = Task.objects.filter(
            user=self.request.user,
            deleted=False
        ).order_by("completed", "priority")

        if status:
            tasks = tasks.filter(completed=status == "completed")

        return tasks

    def get_context_data(self, **kwargs):
        context = super(GenericTaskView, self).get_context_data(**kwargs)
        base_query = Task.objects.filter(user=self.request.user, deleted=False)
        context['total'] = base_query.count()
        context['completed'] = base_query.filter(completed=True).count()

        return context


class GenericTaskCreateView(AuthorizedTaskManager, CreateView):
    model = Task
    template_name = "task_create.html"
    form_class = TaskCreateForm
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.__cascade_priority(self.object.priority)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def __cascade_priority(self, priority):
        cur_priority = priority
        while True:
            filter_task = Task.objects.filter(
                deleted=False,
                priority=cur_priority,
                user=self.request.user,
                completed=False
            )

            is_existing_priority = filter_task.exists()

            if not is_existing_priority:
                break
            cur_priority += 1

        Task.objects.filter(
            deleted=False,
            priority__gte=priority,
            priority__lte=cur_priority,
            completed=False,
            user=self.request.user
        ).update(priority=F('priority')+1)


class GenericTaskUpdateView(AuthorizedTaskManager, UpdateView):
    model = Task
    template_name = "task_update.html"
    form_class = TaskCreateForm
    success_url = "/tasks"


class GenericTaskDeleteView(AuthorizedTaskManager, DeleteView):
    model = Task
    success_url = "/tasks"
    template_name = "task_delete.html"


class GenericTaskDetailView(AuthorizedTaskManager, DetailView):
    model = Task
    template_name = "task_detail.html"
