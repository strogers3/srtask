from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Dashboard views
    path('', views.my_day, name='my_day'),
    path('upcoming/', views.upcoming, name='upcoming'),
    path('anytime/', views.anytime, name='anytime'),

    # Task CRUD
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/toggle/', views.task_toggle, name='task_toggle'),
    path('tasks/<int:pk>/toggle-my-day/', views.task_toggle_my_day, name='task_toggle_my_day'),

    # Task Steps
    path('tasks/<int:task_pk>/steps/create/', views.step_create, name='step_create'),
    path('steps/<int:pk>/toggle/', views.step_toggle, name='step_toggle'),
    path('steps/<int:pk>/delete/', views.step_delete, name='step_delete'),

    # Task Notes
    path('tasks/<int:task_pk>/notes/create/', views.note_create, name='note_create'),
    path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('notes/<int:pk>/pin/', views.note_toggle_pin, name='note_toggle_pin'),

    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),

    # Areas
    path('areas/', views.area_list, name='area_list'),
    path('areas/create/', views.area_create, name='area_create'),
    path('areas/<int:pk>/', views.area_detail, name='area_detail'),
    path('areas/<int:pk>/edit/', views.area_edit, name='area_edit'),
    path('areas/<int:pk>/delete/', views.area_delete, name='area_delete'),

    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:pk>/', views.tag_detail, name='tag_detail'),
    path('tags/<int:pk>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:pk>/delete/', views.tag_delete, name='tag_delete'),
]
