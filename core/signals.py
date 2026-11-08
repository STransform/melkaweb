from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings

@receiver(user_logged_in)
def limit_user_sessions(sender, user, request, **kwargs):
    """
    This signal function triggers each time a user logs in. 
    It begins by selecting all active sessions of the currently logged-in user. 
    If these sessions surpass the maximum allowed concurrent sessions, as specified in the settings, it proceeds to delete the older sessions.
    """

    # get the number of maximum allowed session for a user from setting, or use 2 as default
    max_allowed_session = getattr(settings, 'MAX_ALLOWED_CONCURRENT_SESSIONS', 2)
    # Fetch all active sessions by the order of their expire date
    all_active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).order_by('expire_date').reverse()
    # Start user sessions counter from 0
    user_session_counter = 0 
    # For each session check if it is a session of the current logged in user, and delete if maximum allowed session counter is exceeded.
    for session in all_active_sessions:
        # Decode session data to get user id
        data = session.get_decoded() 
        # If the user id of the this session is the same as the logged in user 
        if data.get('_auth_user_id', None) == str(user.id):
            # Increment session counter by 1
            user_session_counter += 1
            # If maximum allowed session counter is exceeded delete old sessions
            if user_session_counter >= max_allowed_session:
                session.delete() 
    
            
        
    