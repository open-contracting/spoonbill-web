import axios from 'axios';

export default {
    sendFile(files, cancelToken, onUploadProgress) {
        // let filesArr = [...files];
        return axios.post('uploads/', files, {
            cancelToken,
            onUploadProgress,
        });
    },

    sendUrl(urls) {
        return axios.post('urls/', {
            urls,
        });
    },

    getUploadInfo(id) {
        return axios.get('uploads/' + id + '/');
    },

    getUploadInfoByUrl(id) {
        return axios.get('urls/' + id + '/');
    },

    /**
     * Sends POST request to create selections
     * @param { 'urls' | 'uploads' } type
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

    /**
     * Sends POST request to create selections with OCDS Lite
     * @param type { 'urls' | 'uploads' } type
     * @param id { string } id - id of upload or URL
     */
    createOcdsLiteSelections(type, id) {
        return axios.post(`${type}/${id}/selections/`, {
            kind: 'ocds_lite',
        });
    },

    /**
     * Get selections
     * @param { 'urls' | 'uploads' } type
     * @param { string } uploadId - id of upload or URL
     * @param { string } selectionsId - id of selection
     */
    getSelections(type, uploadId, selectionsId) {
        return axios.get(`${type}/${uploadId}/selections/${selectionsId}/`);
    },

    /**
     * Get table's preview
     * @param { 'urls' | 'uploads' } type
     * @param { string } uploadId - id of upload or URL
     * @param { string } selectionsId - id of selection
     * @param { string } tableId - id of table
     */
    getTablePreview(type, uploadId, selectionsId, tableId) {
        return axios.get(`${type}/${uploadId}/selections/${selectionsId}/tables/${tableId}/preview/`);
    },

    /**
     * Changes split status of table
     * @param { 'urls' | 'uploads' } type
     * @param { string } uploadId - id of upload or URL
     * @param { string } selectionsId - id of selection
     * @param { string } tableId - id of table
     * @param { boolean } value
     */
    changeSplitStatus(type, uploadId, selectionsId, tableId, value) {
        return axios.patch(`${type}/${uploadId}/selections/${selectionsId}/tables/${tableId}/`, {
            split: value,
        });
    },

    /**
     * Changes include status of table
     * @param { 'urls' | 'uploads' } type
     * @param { string } uploadId - id of upload or URL
     * @param { string } selectionsId - id of selection
     * @param { string } tableId - id of table
     * @param { boolean } value
     */
    changeIncludeStatus(type, uploadId, selectionsId, tableId, value) {
        return axios.patch(`${type}/${uploadId}/selections/${selectionsId}/tables/${tableId}/`, {
            include: value,
        });
    },

    /**
     * Update table's name
     * @param { 'urls' | 'uploads' } type
     * @param { string } uploadId - id of upload or URL
     * @param { string } selectionsId - id of selection
     * @param { string } tableId - id of table
     * @param { string } heading
     */
    updateTableHeading(type, uploadId, selectionsId, tableId, heading) {
        return axios.patch(`${type}/${uploadId}/selections/${selectionsId}/tables/${tableId}/`, {
            heading,
        });
    },

    /**
     * Change heading type of selection
     * @param { 'urls' | 'uploads' } type
     * @param { string } uploadId - id of upload or URL
     * @param { string } selectionsId - id of selection
     * @param { string } value
     */
    changeHeadingsType(type, uploadId, selectionsId, value) {
        return axios.patch(`${type}/${uploadId}/selections/${selectionsId}/`, {
            headings_type: value,
        });
    },

    /**
     * Create flatten
     * @param { 'urls' | 'uploads' } type
     * @param { string } uploadId - id of upload or URL
     * @param { string } selectionsId - id of selection
     * @param { 'csv' | 'xlsx' } format
     */
    createFlatten(type, uploadId, selectionsId, format) {
        return axios.post(`${type}/${uploadId}/selections/${selectionsId}/flattens/`, {
            export_format: format,
        });
    },

    /**
     * Schedule flatten generation
     * @param { 'urls' | 'uploads' } type
     * @param { string } uploadId - id of upload or URL
     * @param { string } selectionsId - id of selection
     * @param { string } flattenId
     */
    scheduleFlattenGeneration(type, uploadId, selectionsId, flattenId) {
        return axios.patch(`${type}/${uploadId}/selections/${selectionsId}/flattens/${flattenId}/`, {
            status: 'scheduled',
        });
    },
};
