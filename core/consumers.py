import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ValidationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["upload_id"]
        self.room_group_name = f"datasource_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def task_validate(self, event):
        await self.send(text_data=json.dumps(event))

    async def task_download_data_source(self, event):
        await self.send(text_data=json.dumps(event))
