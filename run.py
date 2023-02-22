# run.py
import os
from waitress import serve
from student_management_system.wsgi import application  as app# Import your app

# Run from the same directory as this script
this_files_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_files_dir)

# `url_prefix` is optional, but useful if you are serving app on a sub-dir
# behind a reverse-proxy.
serve(app, host='127.0.0.1', port=80) #, url_prefix='/my-app')