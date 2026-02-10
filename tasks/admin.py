from django.contrib import admin
from .models import (
    Area, Project, Tag, Task, TaskStep, TaskNote,
    ActivityLog, GoogleCalendarConnection, GoogleCalendarSync,
    SavedFilter, PomodoroSession,
)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'sort_order']
    list_filter = ['user']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'area', 'is_completed', 'color']
    list_filter = ['user', 'is_completed', 'area']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color']
    list_filter = ['user']


class TaskStepInline(admin.TabularInline):
    model = TaskStep
    extra = 0


class TaskNoteInline(admin.StackedInline):
    model = TaskNote
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'due_date', 'project', 'is_my_day']
    list_filter = ['user', 'status', 'priority', 'is_my_day', 'project']
    search_fields = ['title', 'description']
    inlines = [TaskStepInline, TaskNoteInline]


@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    list_display = ['title', 'task', 'is_completed', 'sort_order']


@admin.register(TaskNote)
class TaskNoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'task', 'is_pinned', 'created_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'action', 'created_at']
    list_filter = ['action']


@admin.register(GoogleCalendarConnection)
class GoogleCalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'calendar_id', 'sync_all_tasks']


@admin.register(GoogleCalendarSync)
class GoogleCalendarSyncAdmin(admin.ModelAdmin):
    list_display = ['task', 'sync_status', 'last_synced_at']


@admin.register(SavedFilter)
class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']


@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ['task', 'duration_minutes', 'started_at', 'was_completed']
