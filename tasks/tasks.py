from datetime import datetime, timedelta, timezone
from django.db.models import Q

from django.core.mail import send_mail
from tasks.models import Reports, Task
from task_manager.celery import app
from celery import Celery
from celery.decorators import periodic_task

# Periodic Task


@app.task
def send_periodic_email():
    start = datetime.now(timezone.utc) - timedelta(days=1)
    reports = Reports.objects.select_for_update().filter(
        Q(last_sent__lt=start) | Q(last_sent__isnull=True)
    )
    print(reports, start)
    for report in reports:
        send_mail("Your Tasks Report", "generate_email(report.user)",
                  "no-reply@task.com", [report.user.email])
        report.last_sent = datetime.now(timezone.utc).replace(hour=report.timing.hour, minute=report.timing.minute,
                                                              second=report.timing.second)
        print(
            f"{datetime.now(timezone.utc)} [REPORT SENT]] : ", report.user.email)
        report.save()


def generate_email(user):
    user_tasks = Task.objects.filter(user=user, deleted=False)
    pending_tasks = user_tasks.filter(status="PENDING").count()
    in_progress_tasks = user_tasks.filter(status="IN_PROGRESS").count()
    completed_tasks = user_tasks.filter(status="COMPLETED").count()
    cancelled_tasks = user_tasks.filter(status="CANCELLED").count()

    email = f"""
        <h3> Hi {user.username} </h3>,
        <h1> Your tasks report </h1>
        <p> You have {pending_tasks} pending tasks </p>
        <p> You have {in_progress_tasks} in progress tasks </p>
        <p> You have {completed_tasks} completed tasks </p>
        <p> You have {cancelled_tasks} cancelled tasks </p>
    """
    return email


app.conf.beat_schedule = {"send-report-email": {
    'task': 'tasks.tasks.send_periodic_email',
    'schedule': 5,
},
}
