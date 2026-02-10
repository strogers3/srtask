from django.conf import settings
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Abstract base with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Area(BaseModel):
    """Life category (Work, Personal, Health). Not completable."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='areas')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#6366f1')  # hex color
    icon = models.CharField(max_length=50, blank=True, default='')
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name


class Project(BaseModel):
    """A project that organizes tasks. Can be completed."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    color = models.CharField(max_length=7, default='#3b82f6')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def complete(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=['is_completed', 'completed_at', 'updated_at'])


class Tag(BaseModel):
    """Global label that can be applied to tasks."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#8b5cf6')

    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name


class Task(BaseModel):
    """Core task model."""

    class Priority(models.IntegerChoices):
        P1 = 1, 'Priority 1 (Urgent)'
        P2 = 2, 'Priority 2 (High)'
        P3 = 3, 'Priority 3 (Medium)'
        P4 = 4, 'Priority 4 (Low)'

    PRIORITY_COLORS = {
        1: '#ef4444',  # red
        2: '#f59e0b',  # amber
        3: '#3b82f6',  # blue
        4: '#9ca3af',  # gray
    }

    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default='')
    priority = models.IntegerField(choices=Priority.choices, default=Priority.P4)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # My Day
    is_my_day = models.BooleanField(default=False)
    my_day_date = models.DateField(null=True, blank=True)

    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=500, blank=True, default='')  # iCalendar RRULE

    # Google Calendar
    sync_to_google_calendar = models.BooleanField(default=False)

    # Estimates
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)

    # Tags
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')

    # Ordering
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', '-priority', 'due_date', 'created_at']

    def __str__(self):
        return self.title

    @property
    def priority_color(self):
        return self.PRIORITY_COLORS.get(self.priority, '#9ca3af')

    @property
    def is_overdue(self):
        if self.due_date and self.status != self.Status.COMPLETED:
            return self.due_date < timezone.now().date()
        return False

    @property
    def steps_progress(self):
        total = self.steps.count()
        if total == 0:
            return None
        done = self.steps.filter(is_completed=True).count()
        return f"{done}/{total}"

    def complete(self):
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def uncomplete(self):
        self.status = self.Status.TODO
        self.completed_at = None
        self.save(update_fields=['status', 'completed_at', 'updated_at'])


class TaskStep(BaseModel):
    """Simple checklist item within a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=300)
    is_completed = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return self.title


class TaskNote(BaseModel):
    """Rich text note attached to a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200, blank=True, default='')
    content_html = models.TextField(default='')
    content_json = models.JSONField(default=dict, blank=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title or f"Note on {self.task.title}"


class ActivityLog(BaseModel):
    """Change history for a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50)  # e.g., 'created', 'completed', 'edited'
    detail = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.task.title}"


class GoogleCalendarConnection(BaseModel):
    """User's Google Calendar OAuth2 connection."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='google_calendar_connection')
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()
    calendar_id = models.CharField(max_length=200, default='primary')
    sync_all_tasks = models.BooleanField(default=False)
    remove_on_complete = models.BooleanField(default=True)

    def __str__(self):
        return f"Google Calendar - {self.user.email}"


class GoogleCalendarSync(BaseModel):
    """Tracks sync status for a task to Google Calendar."""

    class SyncStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SYNCED = 'synced', 'Synced'
        FAILED = 'failed', 'Failed'

    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='calendar_sync')
    google_event_id = models.CharField(max_length=300, blank=True, default='')
    last_synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING)
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Sync: {self.task.title} ({self.sync_status})"


class SavedFilter(BaseModel):
    """Named filter query saved by user."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_filters')
    name = models.CharField(max_length=100)
    filter_config = models.JSONField(default=dict)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PomodoroSession(BaseModel):
    """Pomodoro work session linked to a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='pomodoro_sessions')
    duration_minutes = models.PositiveIntegerField(default=25)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    was_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Pomodoro: {self.task.title} ({self.duration_minutes}min)"
