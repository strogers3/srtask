from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from tasks.models import Area, Project, Tag, Task
from tasks.forms import AreaForm, ProjectForm, TagForm


@login_required
def project_list(request):
    """List all projects."""
    projects = Project.objects.filter(user=request.user, is_completed=False).select_related('area')
    areas = Area.objects.filter(user=request.user)
    context = {
        'projects': projects,
        'areas': areas,
        'view_name': 'projects',
        'page_title': 'Projects',
    }
    return render(request, 'tasks/project_list.html', context)


@login_required
def project_create(request):
    """Create a new project."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            if request.htmx:
                return render(request, 'partials/project_item.html', {'project': project})
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
        form.fields['area'].queryset = request.user.areas.all()

    if request.htmx:
        return render(request, 'partials/project_form.html', {'form': form})
    return render(request, 'tasks/project_form.html', {'form': form, 'page_title': 'New Project'})


@login_required
def project_detail(request, pk):
    """View project and its tasks."""
    project = get_object_or_404(Project, pk=pk, user=request.user)
    tasks = Task.objects.filter(
        project=project,
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
    ).prefetch_related('tags', 'steps')

    context = {
        'project': project,
        'tasks': tasks,
        'view_name': 'project_detail',
        'page_title': project.name,
    }
    return render(request, 'tasks/project_detail.html', context)


@login_required
def project_edit(request, pk):
    """Edit a project."""
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            if request.htmx:
                return render(request, 'partials/project_item.html', {'project': project})
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
        form.fields['area'].queryset = request.user.areas.all()

    if request.htmx:
        return render(request, 'partials/project_form.html', {'form': form, 'project': project})
    return render(request, 'tasks/project_form.html', {'form': form, 'project': project, 'page_title': f'Edit {project.name}'})


@login_required
@require_POST
def project_delete(request, pk):
    """Delete a project."""
    project = get_object_or_404(Project, pk=pk, user=request.user)
    project.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('tasks:project_list')


# Areas

@login_required
def area_list(request):
    """List all areas."""
    areas = Area.objects.filter(user=request.user).prefetch_related('projects')
    context = {
        'areas': areas,
        'view_name': 'areas',
        'page_title': 'Areas',
    }
    return render(request, 'tasks/area_list.html', context)


@login_required
def area_create(request):
    """Create a new area."""
    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            area = form.save(commit=False)
            area.user = request.user
            area.save()
            if request.htmx:
                return render(request, 'partials/area_item.html', {'area': area})
            return redirect('tasks:area_list')
    else:
        form = AreaForm()

    if request.htmx:
        return render(request, 'partials/area_form.html', {'form': form})
    return render(request, 'tasks/area_form.html', {'form': form, 'page_title': 'New Area'})


@login_required
def area_detail(request, pk):
    """View area and its projects."""
    area = get_object_or_404(Area, pk=pk, user=request.user)
    projects = area.projects.filter(is_completed=False)
    context = {
        'area': area,
        'projects': projects,
        'view_name': 'area_detail',
        'page_title': area.name,
    }
    return render(request, 'tasks/area_detail.html', context)


@login_required
def area_edit(request, pk):
    """Edit an area."""
    area = get_object_or_404(Area, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            if request.htmx:
                return render(request, 'partials/area_item.html', {'area': area})
            return redirect('tasks:area_detail', pk=area.pk)
    else:
        form = AreaForm(instance=area)

    if request.htmx:
        return render(request, 'partials/area_form.html', {'form': form, 'area': area})
    return render(request, 'tasks/area_form.html', {'form': form, 'area': area, 'page_title': f'Edit {area.name}'})


@login_required
@require_POST
def area_delete(request, pk):
    """Delete an area."""
    area = get_object_or_404(Area, pk=pk, user=request.user)
    area.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('tasks:area_list')


# Tags

@login_required
def tag_list(request):
    """List all tags."""
    tags = Tag.objects.filter(user=request.user)
    context = {
        'tags': tags,
        'view_name': 'tags',
        'page_title': 'Tags',
    }
    return render(request, 'tasks/tag_list.html', context)


@login_required
def tag_create(request):
    """Create a new tag."""
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            if request.htmx:
                return render(request, 'partials/tag_item.html', {'tag': tag})
            return redirect('tasks:tag_list')
    else:
        form = TagForm()

    if request.htmx:
        return render(request, 'partials/tag_form.html', {'form': form})
    return render(request, 'tasks/tag_form.html', {'form': form, 'page_title': 'New Tag'})


@login_required
def tag_detail(request, pk):
    """View tasks with this tag."""
    tag = get_object_or_404(Tag, pk=pk, user=request.user)
    tasks = Task.objects.filter(
        user=request.user,
        tags=tag,
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
    ).select_related('project').prefetch_related('tags', 'steps')

    context = {
        'tag': tag,
        'tasks': tasks,
        'view_name': 'tag_detail',
        'page_title': f'#{tag.name}',
    }
    return render(request, 'tasks/tag_detail.html', context)


@login_required
def tag_edit(request, pk):
    """Edit a tag."""
    tag = get_object_or_404(Tag, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            if request.htmx:
                return render(request, 'partials/tag_item.html', {'tag': tag})
            return redirect('tasks:tag_list')
    else:
        form = TagForm(instance=tag)

    if request.htmx:
        return render(request, 'partials/tag_form.html', {'form': form, 'tag': tag})
    return render(request, 'tasks/tag_form.html', {'form': form, 'tag': tag, 'page_title': f'Edit #{tag.name}'})


@login_required
@require_POST
def tag_delete(request, pk):
    """Delete a tag."""
    tag = get_object_or_404(Tag, pk=pk, user=request.user)
    tag.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('tasks:tag_list')
