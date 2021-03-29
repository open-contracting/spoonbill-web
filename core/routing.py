from django.urls import re_path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import consumers, views

router = DefaultRouter()
router.register(r"uploads", views.UploadViewSet, basename="uploads")
router.register(r"urls", views.URLViewSet, basename="urls")

upload_selection_router = routers.NestedSimpleRouter(router, r"uploads", lookup="upload")
upload_selection_router.register(r"selections", views.DataSelectionViewSet, basename="uploads-selections")

url_selection_router = routers.NestedSimpleRouter(router, r"urls", lookup="url")
url_selection_router.register(r"selections", views.DataSelectionViewSet, basename="urls-selections")

websocket_urlpatterns = [
    re_path(r"ws/api/(?P<upload_id>[0-9a-f-]+)/$", consumers.ValidationConsumer.as_asgi()),
]
