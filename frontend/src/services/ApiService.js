import axios from 'axios';

export default {
    sendFile(file) {
        return axios.post('uploads/', file);
    },
};
