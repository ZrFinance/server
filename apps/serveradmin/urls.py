from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *

router = DefaultRouter(trailing_slash=False)
router.register('', ServerAdmin, base_name='serveradmin')

urlpatterns = [
    path('', include(router.urls))
]