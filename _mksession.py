from importlib import import_module
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, HASH_SESSION_KEY
from django.urls import reverse

U = get_user_model()
u = U.objects.filter(user_type='1').first() or U.objects.first()

engine = import_module(settings.SESSION_ENGINE)
s = engine.SessionStore()
s.create()
s[SESSION_KEY] = str(u.pk)
s[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
s[HASH_SESSION_KEY] = u.get_session_auth_hash()
s.save()
print("SESSID", s.session_key)
print("COOKIENAME", settings.SESSION_COOKIE_NAME)
print("USER", getattr(u, 'username', None), "TYPE", getattr(u, 'user_type', None))
for name in ('admin_home', 'admin_profile', 'dashboard'):
    try:
        print(name.upper(), reverse(name))
    except Exception as e:
        print(name.upper() + "_ERR", e)
