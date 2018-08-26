#!/usr/bin/env python
import sys
from os.path import abspath, dirname, join

from django.conf import settings
from django.core.management import execute_from_command_line


project_dir = dirname(abspath(__file__))
sys.path.insert(0, dirname(project_dir))


settings.configure(
    DEBUG=True,
    SECRET_KEY='A-random-secret-key!',
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': join(project_dir, 'db.sqlite3'),
        },
    },
    INSTALLED_APPS=['test_project'],
)


if __name__ == "__main__":
    execute_from_command_line(sys.argv)
