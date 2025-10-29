from django.urls import path
from .views import MPCreatePreferenceView

urlpatterns = [
    path('mp/preference/', MPCreatePreferenceView.as_view(), name='mp-create-preference'),
]
