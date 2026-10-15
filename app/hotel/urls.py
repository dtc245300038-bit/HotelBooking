
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


def metrics_view(request):
    metrics_data = generate_latest()
    return HttpResponse(
        metrics_data,
        content_type=CONTENT_TYPE_LATEST,
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking.urls')),
    path('metrics', metrics_view, name='metrics'),
]
