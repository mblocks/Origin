# -*- coding: utf-8 -*-
from .welcome import router as welcome
from .admin.apps import router as admin_apps
from .admin.users import router as admin_users
from .admin.templates import router as templates
from .authorized import router as authorized
from .settings import router as settings
