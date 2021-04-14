from django.conf import settings
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

url_table_router = routers.NestedSimpleRouter(url_selection_router, r"selections", lookup="selection")
url_table_router.register(r"tables", views.TableViewSet, basename="urls-selections-tables")

upload_table_router = routers.NestedSimpleRouter(upload_selection_router, r"selections", lookup="selection")
upload_table_router.register(r"tables", views.TableViewSet, basename="uploads-selections-tables")

url_preview_router = routers.NestedSimpleRouter(url_table_router, r"tables", lookup="table")
url_preview_router.register(r"preview", views.TablePreviewViewSet, basename="urls-selections-preview")

upload_preview_router = routers.NestedSimpleRouter(upload_table_router, r"tables", lookup="table")
upload_preview_router.register(r"preview", views.TablePreviewViewSet, basename="uploads-selections-preview")

prefix = "/" if not settings.API_PREFIX else settings.API_PREFIX
websocket_urlpatterns = [
    re_path(r"{prefix}ws/(?P<upload_id>[0-9a-f-]+)/$".format(prefix=prefix), consumers.ValidationConsumer.as_asgi()),
]
