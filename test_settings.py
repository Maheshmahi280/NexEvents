import os
import sys
import django

sys.path.insert(0, 'd:/Hackrivals/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.conf import settings

print('=== Django Configuration ===')
print(f'TEMPLATES DIRS: {settings.TEMPLATES[0]["DIRS"]}')
print(f'STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
print('')
print('=== Checking Paths ===')
for template_dir in settings.TEMPLATES[0]['DIRS']:
    exists = os.path.exists(template_dir)
    print(f'✓ Templates exist: {exists}')
    print(f'  Path: {template_dir}')
    if exists:
        files = os.listdir(template_dir)
        print(f'  Files: {", ".join(files[:3])}...')

for static_dir in settings.STATICFILES_DIRS:
    exists = os.path.exists(static_dir)
    print(f'✓ Static exists: {exists}')
    print(f'  Path: {static_dir}')
    if exists:
        contents = os.listdir(static_dir)
        print(f'  Contents: {", ".join(contents)}')
