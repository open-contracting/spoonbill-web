from django.conf.urls import url
from django.urls import include

from core.routing import router

urlpatterns = [url(r"", include((router.urls, "core")))]
