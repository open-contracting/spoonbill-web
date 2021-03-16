from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/api/(?P<upload_id>[0-9a-f-]+)/$", consumers.ValidationConsumer.as_asgi()),
]
