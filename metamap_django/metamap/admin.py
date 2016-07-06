from django.contrib import admin
from .models import ETL, TblBlood

# Register your models here.

admin.site.register(TblBlood)
admin.site.register(ETL)