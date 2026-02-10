from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone

from tasks.models import Task, TaskStep, ActivityLog
from tasks.forms import TaskForm, TaskStepForm


@login_required
def task_create(request):
    """Create a new task."""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()
            ActivityLog.objects.create(task=task, action='created', detail='Task created')

            if request.htmx:
                return render(request, 'partials/task_item.html', {'task': task})
            return redirect('tasks:my_day')
    else:
        form = TaskForm()
        form.fields['project'].queryset = request.user.projects.filter(is_completed=False)
        form.fields['tags'].queryset = request.user.tags.all()

    if request.htmx:
        return render(request, 'partials/task_form.html', {'form': form, 'inline_form': True})
    return render(request, 'tasks/task_form.html', {'form': form, 'page_title': 'New Task'})


@login_required
def task_detail(request, pk):
    """View task details."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    steps = task.steps.all()
    notes = task.notes.all()
    step_form = TaskStepForm()

    context = {
        'task': task,
        'steps': steps,
        'notes': notes,
        'step_form': step_form,
    }
    if request.htmx:
        return render(request, 'partials/task_detail.html', context)
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_edit(request, pk):
    """Edit a task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(task=task, action='edited', detail='Task updated')
            if request.htmx:
                return render(request, 'partials/task_item.html', {'task': task})
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
        form.fields['project'].queryset = request.user.projects.filter(is_completed=False)
        form.fields['tags'].queryset = request.user.tags.all()

    if request.htmx:
        return render(request, 'partials/task_form.html', {'form': form, 'task': task, 'inline_form': True})
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'page_title': 'Edit Task'})


@login_required
@require_POST
def task_delete(request, pk):
    """Delete a task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('tasks:my_day')


@login_required
@require_POST
def task_toggle(request, pk):
    """Toggle task completion."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if task.status == Task.Status.COMPLETED:
        task.uncomplete()
        ActivityLog.objects.create(task=task, action='uncompleted', detail='Task reopened')
    else:
        task.complete()
        ActivityLog.objects.create(task=task, action='completed', detail='Task completed')

    if request.htmx:
        return render(request, 'partials/task_item.html', {'task': task})
    return redirect('tasks:my_day')


@login_required
@require_POST
def task_toggle_my_day(request, pk):
    """Toggle task My Day status."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.is_my_day = not task.is_my_day
    if task.is_my_day:
        task.my_day_date = timezone.now().date()
    task.save(update_fields=['is_my_day', 'my_day_date', 'updated_at'])

    if request.htmx:
        return render(request, 'partials/task_item.html', {'task': task})
    return redirect('tasks:my_day')


# Task Steps

@login_required
@require_POST
def step_create(request, task_pk):
    """Add a step to a task."""
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    form = TaskStepForm(request.POST)
    if form.is_valid():
        step = form.save(commit=False)
        step.task = task
        step.sort_order = task.steps.count()
        step.save()
        if request.htmx:
            return render(request, 'partials/step_item.html', {'step': step, 'task': task})
    return redirect('tasks:task_detail', pk=task_pk)


@login_required
@require_POST
def step_toggle(request, pk):
    """Toggle step completion."""
    step = get_object_or_404(TaskStep, pk=pk, task__user=request.user)
    step.is_completed = not step.is_completed
    step.save(update_fields=['is_completed', 'updated_at'])
    if request.htmx:
        return render(request, 'partials/step_item.html', {'step': step, 'task': step.task})
    return redirect('tasks:task_detail', pk=step.task.pk)


@login_required
@require_POST
def step_delete(request, pk):
    """Delete a step."""
    step = get_object_or_404(TaskStep, pk=pk, task__user=request.user)
    task_pk = step.task.pk
    step.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('tasks:task_detail', pk=task_pk)
