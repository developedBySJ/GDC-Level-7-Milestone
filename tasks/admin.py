from django.contrib import admin

# Register your models here.

from tasks.models import Reports, Task

admin.sites.site.register(Task)
admin.sites.site.register(Reports)
