from django.contrib import admin
from .models import Claim, UserReport
# Register models so they can be managed from the Django admin panel
# This allows administrators to view, add, edit and delete records
# for both the imported LIAR dataset (Claim) and user submitted reports.

admin.site.register(Claim)
admin.site.register(UserReport)
