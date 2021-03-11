import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer


class ValidationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.room_name = self.scope["url_route"]["kwargs"]["upload_id"]
        self.room_group_name = f"validate_data_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # def recieve(self, text_data):
    #     data = json.loads(text_data)

    def task_validate(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"message": message}))
