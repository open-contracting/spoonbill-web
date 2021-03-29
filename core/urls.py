from django.conf.urls import url
from django.urls import include

# from core.routing import router
from core.routing import router, upload_selection_router, upload_table_router, url_selection_router, url_table_router

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^", include(upload_selection_router.urls)),
    url(r"^", include(upload_table_router.urls)),
    url(r"^", include(url_selection_router.urls)),
    url(r"^", include(url_table_router.urls)),
]
