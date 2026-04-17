from django.urls import path
from .views import SiteSettingsRetrieveUpdateView

urlpatterns = [
    # الرابط هيكون /api/core/settings/
    path('settings/', SiteSettingsRetrieveUpdateView.as_view(), name='site-settings'),
]