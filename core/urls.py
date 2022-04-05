from django.urls import include, path

from core.routing import (
    router,
    upload_preview_router,
    upload_selection_router,
    upload_table_router,
    url_preview_router,
    url_selection_router,
    url_table_router,
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(upload_selection_router.urls)),
    path("", include(upload_table_router.urls)),
    path("", include(url_selection_router.urls)),
    path("", include(url_table_router.urls)),
    path("", include(upload_preview_router.urls)),
    path("", include(url_preview_router.urls)),
]
