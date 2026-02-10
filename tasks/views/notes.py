from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from tasks.models import Task, TaskNote
from tasks.forms import TaskNoteForm


@login_required
def note_create(request, task_pk):
    """Add a note to a task."""
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'POST':
        form = TaskNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.task = task
            note.save()
            if request.htmx:
                return render(request, 'partials/note_item.html', {'note': note, 'task': task})
            return redirect('tasks:task_detail', pk=task_pk)
    else:
        form = TaskNoteForm()

    if request.htmx:
        return render(request, 'partials/note_form.html', {'form': form, 'task': task})
    return render(request, 'tasks/note_form.html', {'form': form, 'task': task, 'page_title': 'New Note'})


@login_required
def note_edit(request, pk):
    """Edit a note."""
    note = get_object_or_404(TaskNote, pk=pk, task__user=request.user)
    if request.method == 'POST':
        form = TaskNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            if request.htmx:
                return render(request, 'partials/note_item.html', {'note': note, 'task': note.task})
            return redirect('tasks:task_detail', pk=note.task.pk)
    else:
        form = TaskNoteForm(instance=note)

    if request.htmx:
        return render(request, 'partials/note_form.html', {'form': form, 'note': note, 'task': note.task})
    return render(request, 'tasks/note_form.html', {'form': form, 'note': note, 'task': note.task, 'page_title': 'Edit Note'})


@login_required
@require_POST
def note_delete(request, pk):
    """Delete a note."""
    note = get_object_or_404(TaskNote, pk=pk, task__user=request.user)
    task_pk = note.task.pk
    note.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('tasks:task_detail', pk=task_pk)


@login_required
@require_POST
def note_toggle_pin(request, pk):
    """Toggle note pinned status."""
    note = get_object_or_404(TaskNote, pk=pk, task__user=request.user)
    note.is_pinned = not note.is_pinned
    note.save(update_fields=['is_pinned', 'updated_at'])
    if request.htmx:
        return render(request, 'partials/note_item.html', {'note': note, 'task': note.task})
    return redirect('tasks:task_detail', pk=note.task.pk)
