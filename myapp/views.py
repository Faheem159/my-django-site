from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .models import MaintenanceRequest, UserProfile, Property, TicketMessage, Announcement, RequestPhoto, DirectMessage

# Helper
def is_landlord(user):
    return user.groups.filter(name='Landlord').exists()

# Signup
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm  = request.POST['confirm']
        role     = request.POST['role']

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('/login/?tab=signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('/login/?tab=signup')

        user = User.objects.create_user(username=username, password=password)
        group = Group.objects.get(name=role)
        user.groups.add(group)
        user.save()

        messages.success(request, 'Account created! Please log in.')
        return redirect('login')

    return redirect('login')

# Login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'myapp/login.html')

# Logout
def user_logout(request):
    logout(request)
    return redirect('login')

# Home — redirects based on role
@login_required(login_url='login')
def home(request):
    if is_landlord(request.user):
        return redirect('dashboard')
    else:
        return redirect('tenant_portal')

# Landlord dashboard
@login_required(login_url='login')
def dashboard(request):
    if not is_landlord(request.user):
        return redirect('tenant_portal')

    requests = MaintenanceRequest.objects.all().order_by('-created_at')
    return render(request, 'myapp/dashboard.html', {'requests': requests})

# Tenant portal
@login_required(login_url='login')
def tenant_portal(request):
    if is_landlord(request.user):
        return redirect('dashboard')

    if request.method == 'POST':
        new_request = MaintenanceRequest.objects.create(
            tenant=request.user,
            category=request.POST['category'],
            urgency=request.POST['urgency'],
            description=request.POST['description'],
        )
        for photo in request.FILES.getlist('photos'):
            RequestPhoto.objects.create(request=new_request, photo=photo)
        messages.success(request, 'Request submitted — your landlord has been notified.')
        return redirect('tenant_portal')

    my_requests = MaintenanceRequest.objects.filter(tenant=request.user).order_by('-created_at')
    all_announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'myapp/tenant_portal.html', {
        'my_requests': my_requests,
        'announcements': all_announcements,
    })

# Landlord updates a request status
@login_required(login_url='login')
def update_status(request, pk):
    if not is_landlord(request.user):
        return redirect('tenant_portal')

    maintenance_request = MaintenanceRequest.objects.get(pk=pk)
    if request.method == 'POST':
        maintenance_request.status = request.POST['status']
        maintenance_request.save()
    return redirect('dashboard')

# Profile
@login_required(login_url='login')
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_info':
            request.user.email = request.POST.get('email', '')
            request.user.save()
            messages.success(request, 'Profile updated.')

        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not request.user.check_password(old_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')

        elif action == 'toggle_dark_mode':
            user_profile.dark_mode = not user_profile.dark_mode
            user_profile.save()

        return redirect('profile')

    properties = Property.objects.all() if is_landlord(request.user) else None

    return render(request, 'myapp/profile.html', {
        'user_profile': user_profile,
        'properties': properties,
    })

# Ticket detail
@login_required(login_url='login')
def ticket_detail(request, pk):
    ticket = MaintenanceRequest.objects.get(pk=pk)
    messages_list = ticket.messages.all().order_by('created_at')

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            TicketMessage.objects.create(
                request=ticket,
                sender=request.user,
                message=message
            )
        return redirect('ticket_detail', pk=pk)

    return render(request, 'myapp/ticket_detail.html', {
        'ticket': ticket,
        'messages_list': messages_list,
    })

# Announcements
@login_required(login_url='login')
def announcements(request):
    if not is_landlord(request.user):
        return redirect('tenant_portal')

    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        if title and body:
            Announcement.objects.create(landlord=request.user, title=title, body=body)
        return redirect('announcements')

    all_announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'myapp/announcements.html', {'announcements': all_announcements})

# Delete announcement
@login_required(login_url='login')
def delete_announcement(request, pk):
    if not is_landlord(request.user):
        return redirect('tenant_portal')
    announcement = Announcement.objects.get(pk=pk)
    announcement.delete()
    return redirect('announcements')

# Landlord chat list
@login_required(login_url='login')
def chat_list(request):
    if not is_landlord(request.user):
        return redirect('tenant_portal')

    tenants = User.objects.filter(groups__name='Tenant')
    tenant_data = []
    for tenant in tenants:
        last_msg = DirectMessage.objects.filter(
            sender__in=[request.user, tenant],
            receiver__in=[request.user, tenant]
        ).order_by('-created_at').first()
        tenant_data.append({
            'tenant': tenant,
            'last_message': last_msg,
        })

    return render(request, 'myapp/chat_list.html', {'tenant_data': tenant_data})

# Landlord chat detail
@login_required(login_url='login')
def chat_detail(request, tenant_id):
    if not is_landlord(request.user):
        return redirect('tenant_portal')
    tenant = User.objects.get(pk=tenant_id)
    chat_messages = DirectMessage.objects.filter(
        sender__in=[request.user, tenant],
        receiver__in=[request.user, tenant]
    ).order_by('created_at')

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            DirectMessage.objects.create(
                sender=request.user,
                receiver=tenant,
                message=message
            )
        return redirect('chat_detail', tenant_id=tenant_id)

    return render(request, 'myapp/chat_detail.html', {
        'tenant': tenant,
        'chat_messages': chat_messages,
    })

# Tenant chat
@login_required(login_url='login')
def tenant_chat(request):
    if is_landlord(request.user):
        return redirect('dashboard')

    landlord = User.objects.filter(groups__name='Landlord').first()

    chat_messages = DirectMessage.objects.filter(
        sender__in=[request.user, landlord],
        receiver__in=[request.user, landlord]
    ).order_by('created_at')

    if request.method == 'POST':
        message = request.POST.get('message')
        if message and landlord:
            DirectMessage.objects.create(
                sender=request.user,
                receiver=landlord,
                message=message
            )
        return redirect('tenant_chat')

    return render(request, 'myapp/tenant_chat.html', {
        'landlord': landlord,
        'chat_messages': chat_messages,
    })