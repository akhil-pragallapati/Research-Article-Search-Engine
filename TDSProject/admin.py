from django.contrib import admin
from TDSProject.models import DB1
from TDSProject.models import Q
from TDSProject.models import operators

admin.site.register(DB1)
admin.site.register(Q)
admin.site.register(operators)