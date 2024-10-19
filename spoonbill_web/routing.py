from django.urls import re_path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from spoonbill_web import consumers, views

router = DefaultRouter()
router.register(r"uploads", views.UploadViewSet, basename="uploads")
router.register(r"urls", views.URLViewSet, basename="urls")

upload_selection_router = routers.NestedSimpleRouter(router, r"uploads", lookup="upload")
upload_selection_router.register(r"selections", views.DataSelectionViewSet, basename="uploads-selections")

url_selection_router = routers.NestedSimpleRouter(router, r"urls", lookup="url")
url_selection_router.register(r"selections", views.DataSelectionViewSet, basename="urls-selections")

url_table_router = routers.NestedSimpleRouter(url_selection_router, r"selections", lookup="selection")
url_table_router.register(r"tables", views.TableViewSet, basename="urls-selections-tables")
url_table_router.register(r"flattens", views.FlattenViewSet, basename="urls-selections-flattens")

upload_table_router = routers.NestedSimpleRouter(upload_selection_router, r"selections", lookup="selection")
upload_table_router.register(r"tables", views.TableViewSet, basename="uploads-selections-tables")
upload_table_router.register(r"flattens", views.FlattenViewSet, basename="uploads-selections-flattens")

url_preview_router = routers.NestedSimpleRouter(url_table_router, r"tables", lookup="table")
url_preview_router.register(r"preview", views.TablePreviewViewSet, basename="urls-selections-preview")

upload_preview_router = routers.NestedSimpleRouter(upload_table_router, r"tables", lookup="table")
upload_preview_router.register(r"preview", views.TablePreviewViewSet, basename="uploads-selections-preview")

websocket_urlpatterns = [
    re_path(r"api/ws/(?P<upload_id>[0-9a-f-]+)/$", consumers.ValidationConsumer.as_asgi()),
]
