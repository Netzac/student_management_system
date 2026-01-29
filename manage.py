#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import sys
from types import ModuleType

# Create a fake distutils.command.upload module in memory
if 'distutils.command.upload' not in sys.modules:
    d = ModuleType('distutils')
    dc = ModuleType('distutils.command')
    dcu = ModuleType('distutils.command.upload')
    
    sys.modules['distutils'] = d
    sys.modules['distutils.command'] = dc
    sys.modules['distutils.command.upload'] = dcu
    
    # Give it a fake 'upload' class so it doesn't crash on attribute access
    class Upload: pass
    dcu.upload = Upload

import os
# ... rest of your manage.py



def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
