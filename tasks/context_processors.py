from tasks.models import Project, Area, Tag


def sidebar_data(request):
    """Provide sidebar navigation data to all templates."""
    if not request.user.is_authenticated:
        return {}

    return {
        'sidebar_projects': Project.objects.filter(user=request.user, is_completed=False)[:20],
        'sidebar_areas': Area.objects.filter(user=request.user)[:20],
        'sidebar_tags': Tag.objects.filter(user=request.user)[:20],
    }
