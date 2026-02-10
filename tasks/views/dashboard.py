from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from tasks.models import Task


@login_required
def my_day(request):
    """My Day view - daily focus list."""
    today = timezone.now().date()
    tasks = Task.objects.filter(
        user=request.user,
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
    ).filter(
        # Tasks explicitly added to My Day or due today
        is_my_day=True,
    ) | Task.objects.filter(
        user=request.user,
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
        due_date=today,
    )
    tasks = tasks.distinct().select_related('project').prefetch_related('tags', 'steps')

    context = {
        'tasks': tasks,
        'view_name': 'my_day',
        'page_title': 'My Day',
        'today': today,
    }
    return render(request, 'tasks/my_day.html', context)


@login_required
def upcoming(request):
    """Upcoming view - future tasks grouped by date."""
    today = timezone.now().date()
    tasks = Task.objects.filter(
        user=request.user,
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
        due_date__gte=today,
    ).select_related('project').prefetch_related('tags', 'steps').order_by('due_date', 'sort_order')

    context = {
        'tasks': tasks,
        'view_name': 'upcoming',
        'page_title': 'Upcoming',
        'today': today,
    }
    return render(request, 'tasks/upcoming.html', context)


@login_required
def anytime(request):
    """Anytime view - tasks with no due date."""
    tasks = Task.objects.filter(
        user=request.user,
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
        due_date__isnull=True,
    ).select_related('project').prefetch_related('tags', 'steps')

    context = {
        'tasks': tasks,
        'view_name': 'anytime',
        'page_title': 'Anytime',
    }
    return render(request, 'tasks/anytime.html', context)
