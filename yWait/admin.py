from django.contrib import admin
from .models import ComparisonSet, Location, trafficData

# Register your models here.
admin.site.register(ComparisonSet)
admin.site.register(Location)
admin.site.register(trafficData)