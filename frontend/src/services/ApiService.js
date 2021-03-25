import axios from 'axios';

export default {
    sendFile(file, cancelToken) {
        return axios.post('uploads/', file, {
            cancelToken,
        });
    },

    sendUrl(url) {
        return axios.post('urls/', {
            url,
        });
    },
};
