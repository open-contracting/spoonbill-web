from django.urls import re_path
from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin

from . import consumers, views


class NestedDefaultRouter(NestedRouterMixin, DefaultRouter):
    pass


router = NestedDefaultRouter()
uploads_router = router.register(r"uploads", views.UploadViewSet, basename="upload")
uploads_router.register(
    r"selections", views.DataSelectionViewSet, basename="upload-selection", parents_query_lookups=["upload"]
)

urls_router = router.register(r"urls", views.URLViewSet, basename="url")
urls_router.register(
    r"selections", views.DataSelectionViewSet, basename="url-selection", parents_query_lookups=["url"]
)


websocket_urlpatterns = [
    re_path(r"ws/api/(?P<upload_id>[0-9a-f-]+)/$", consumers.ValidationConsumer.as_asgi()),
]
