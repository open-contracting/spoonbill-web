import pytest

from core.models import Upload
from core.serializers import UploadSerializer


@pytest.mark.django_db
class TestUpload:

    def test_create_upload_wo_file(self, client):
        response = client.post('/uploads/', {'attr': 'value'})
        assert response.status_code == 400
        assert response.json() == {'detail': 'File is required'}

    def test_create_upload_successful(self, client, dataset, cleanup_upload_task, validation_task):
        response = client.post('/uploads/', {'file': dataset})
        assert response.status_code == 201
        upload = response.json()
        assert set(upload.keys()) == {'expired_at', 'id', 'deleted', 'validation', 'created_at', 'filename'}
        assert set(upload['validation'].keys()) == {'id', 'task_id', 'is_valid', 'errors'}
        assert upload['filename'] == dataset.name.split('/')[-1]
        assert not upload['deleted']

        upload_obj = Upload.objects.get(id=upload['id'])
        validation_task.delay.assert_called_once_with(upload_obj.id, upload_obj.validation.id)
        cleanup_upload_task.apply_async.assert_called_once_with((upload_obj.id,), eta=upload_obj.expired_at)

    def test_get_non_existed_upload(self, client):
        response = client.get('/uploads/some-invalid-id/')
        assert response.status_code == 404
        assert response.json() == {'detail': 'Not found.'}

    def test_get_upload_successful(self, client, upload_obj):
        response = client.get(f'/uploads/{upload_obj.id}/')
        assert response.status_code == 200
        assert UploadSerializer(upload_obj).data == response.json()
