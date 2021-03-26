import axios from 'axios';

export default {
    sendFile(file, cancelToken, onUploadProgress) {
        return axios.post('uploads/', file, {
            cancelToken,
            onUploadProgress,
        });
    },

    sendUrl(url) {
        return axios.post('urls/', {
            url,
        });
    },

    getUploadInfo(id) {
        return axios.get('uploads/' + id);
    },
};
