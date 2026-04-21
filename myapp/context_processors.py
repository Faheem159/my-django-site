from .models import Announcement

def announcements(request):
    if request.user.is_authenticated and not request.user.groups.filter(name='Landlord').exists():
        all_announcements = Announcement.objects.all().order_by('-created_at')
        return {
            'announcements': all_announcements,
            'announcement_count': all_announcements.count()
        }
    return {'announcements': None, 'announcement_count': 0}