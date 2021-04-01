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

    getUploadInfoByUrl(id) {
        return axios.get('urls/' + id);
    },

    /**
     * Sends POST request to create selections
     * @param { 'urls' | 'upload' } type
     * @param { string } id - id of upload or URL
     * @param { string[] } selectedTables - array of tables names
     */
    createSelections(type, id, selectedTables) {
        return axios.post(`${type}/${id}/selections/`, {
            tables: selectedTables.map((tableName) => {
                return { name: tableName };
            }),
        });
    },
};
