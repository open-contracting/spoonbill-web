<template>
    <div>
        <div class="mb-4 d-flex options" :class="{ 'options--disabled': uploadDetails }">
            <div
                class="option"
                :class="{ 'option--selected': option.value === uploadType }"
                v-for="option in options"
                :key="option.value"
                @click="selectUploadType(option.value)"
                v-ripple
            >
                {{ option.title }}
            </div>
        </div>

        <div class="p-relative">
            <upload-file-loading-progress
                v-if="loading.value"
                :cancelable="loading.cancelable"
                :status="loading.status"
                :file-name="loading.fileName"
                :percent="downloadProgress"
                :color="loading.color"
                @cancel="cancelRequest"
            />

            <template v-else>
                <app-dropzone @input="sendFile" v-if="uploadType === 'FILE'" />

                <upload-file-url-input @submit="sendUrl" v-else />
            </template>
        </div>

        <p v-if="!isValid" class="mt-4 text-light-14">
            Note that large files may take a while to process. Please be patient.
        </p>

        <upload-file-options class="mt-15" v-if="isValid" @select="onOptionSelect" />
    </div>
</template>

<script>
import AppDropzone from '@/components/App/AppDropzone';
import UploadFileUrlInput from '@/components/UploadFile/UploadFileUrlInput';
import axios from 'axios';
import ApiService from '@/services/ApiService';
import { UPLOAD_STATUSES, UPLOAD_TYPES } from '@/constants';
import UploadFileLoadingProgress from '@/components/UploadFile/UploadFileLoadingProgress';
import UploadFileOptions from '@/components/UploadFile/UploadFileOptions';

export default {
    name: 'UploadFileInput',

    components: {
        UploadFileOptions,
        UploadFileLoadingProgress,
        UploadFileUrlInput,
        AppDropzone,
    },

    data() {
        return {
            loading: {
                value: false,
                status: null,
                fileName: null,
                cancelable: false,
            },
            cancelTokenSource: null,
            options: [
                {
                    title: 'Upload JSON file',
                    value: UPLOAD_TYPES.FILE,
                },
                {
                    title: 'Supply a URL for JSON',
                    value: UPLOAD_TYPES.URL,
                },
            ],
            /** @type { 'FILE' | 'URL' }*/
            uploadType: UPLOAD_TYPES.FILE,
            fileName: null,
        };
    },

    computed: {
        isValid() {
            return this.$store.state.uploadDetails?.validation?.is_valid;
        },

        uploadDetails() {
            return this.$store.state.uploadDetails;
        },

        downloadProgress() {
            return this.$store.state.downloadProgress;
        },
    },

    watch: {
        uploadDetails: {
            handler(v) {
                if (!v) {
                    this.loading.value = false;
                    return;
                }
                const status = v.status;
                if (status === UPLOAD_STATUSES.QUEUED_VALIDATION) {
                    this.loading = {
                        value: true,
                        status: 'File is queued for validation...',
                        fileName: this.fileName || this.$store.state.uploadDetails.id,
                    };
                }
                if (status === UPLOAD_STATUSES.QUEUED_DOWNLOAD) {
                    this.loading = {
                        value: true,
                        status: 'File is queued for downloading...',
                        fileName: this.fileName || this.$store.state.uploadDetails.id,
                    };
                }
                if (status === UPLOAD_STATUSES.VALIDATION) {
                    this.processValidationStatus();
                }
                if (status === UPLOAD_STATUSES.DOWNLOADING) {
                    this.showLoading(this.fileName || this.$store.state.uploadDetails.id, false);
                }
            },
            immediate: true,
        },
    },

    methods: {
        /**
         * Shows status of validation
         * If validation has failed - shows error message
         * If validation has finished successfully - shows success message and possibility to open next step
         * If validation still in progress - shows progressbar
         */
        processValidationStatus() {
            const upload = this.$store.state.uploadDetails;
            if (upload.validation.is_valid === false) {
                this.uploadType = UPLOAD_TYPES.FILE;
                this.loading.value = false;
                this.$store.commit('openSnackbar', {
                    color: 'error',
                    text:
                        'This file is not compliant with the OCDS schema so cannot be flattened.\n' +
                        'Check your data using the Data Review Tool and resolve the issues before flattening. ',
                });
                this.$store.commit('setUploadDetails', null);
                return;
            }
            if (upload.validation.is_valid === true) {
                this.uploadType = UPLOAD_TYPES.FILE;
                this.loading.value = false;
                this.$store.commit('openSnackbar', {
                    color: 'success',
                    text: 'Now your file is analyzed and ready to use.',
                });
                this.loading = {
                    value: true,
                    status: 'Analysis has been completed',
                    fileName: this.fileName || this.uploadDetails.id,
                    color: '#6C75E1',
                };
                this.$store.commit('setDownloadProgress', 100);
                this.valid = true;
                return;
            }
            this.loading = {
                value: true,
                status: 'File analysis in progress...',
                fileName: this.fileName || this.uploadDetails.id,
                color: '#6C75E1',
            };
        },

        /**
         * Creates axios cancel token which allows to cancel file uploading
         */
        createCancelToken() {
            this.cancelTokenSource = axios.CancelToken.source();
        },

        /**
         * Send file; Emits 'send' event on successful submission
         * @param { File } file
         */
        async sendFile(file) {
            try {
                await this.$store.dispatch('closeConnection');
                this.$store.commit('setUploadDetails', null);
                this.showLoading(file.name, true);
                this.createCancelToken();
                const formData = new FormData();
                formData.append('file', file);
                const { data } = await ApiService.sendFile(formData, this.cancelTokenSource.token, (ev) => {
                    this.$store.commit('setDownloadProgress', Math.floor((ev.loaded * 100) / ev.total));
                });
                this.$store.commit('setDownloadProgress', 0);
                this.$store.commit('setUploadDetails', {
                    ...data,
                    type: UPLOAD_TYPES.FILE,
                });
                this.$store.commit('increaseNumberOfUploads');
                this.$router.push(`/upload-file?file=${data.id}`).catch(() => {});
            } catch (e) {
                console.error(e);
            } finally {
                this.loading.value = false;
                this.cancelTokenSource = null;
            }
        },

        /**
         * Changes selected upload type; Clears messages
         * @param { 'FILE' | 'URL' } type
         */
        selectUploadType(type) {
            this.uploadType = type;
        },

        /**
         * Shows uploading progressbar
         * @param { string } fileName
         * @param { boolean } cancelable
         */
        showLoading(fileName, cancelable) {
            this.loading = {
                value: true,
                status: 'Upload in progress',
                fileName,
                cancelable,
            };
            this.fileName = fileName;
        },

        /**
         * Send url
         * @param { string } url
         */
        async sendUrl(url) {
            try {
                await this.$store.dispatch('closeConnection');
                this.$store.commit('setUploadDetails', null);
                this.showLoading(url, false);
                const { data } = await ApiService.sendUrl(url);
                this.$store.commit('setDownloadProgress', 0);
                this.$store.commit('setUploadDetails', {
                    ...data,
                    type: UPLOAD_TYPES.URL,
                });
                this.$store.commit('increaseNumberOfUploads');
                this.$router.push(`/upload-file?url=${data.id}`).catch(() => {});
            } catch (e) {
                console.error(e);
            } finally {
                this.loading.value = false;
            }
        },

        /**
         * Cancel file sending
         */
        cancelRequest() {
            this.cancelTokenSource.cancel('Canceled by user');
            this.loading.value = false;
        },

        /**
         * Handle option select
         * @param { 'AUTO' | 'MANUAL' } option
         */
        onOptionSelect(option) {
            if (option === 'MANUAL') {
                this.$router.push(`/select-data/?${this.uploadDetails.type.toLowerCase()}=${this.uploadDetails.id}`);
            }
        },
    },
};
</script>

<style scoped lang="scss">
.options {
    .option {
        cursor: pointer;
        padding: 12px 34px;
        background-color: map-get($colors, 'gray-light');
        &--selected {
            background-color: map-get($colors, 'primary');
            color: map-get($colors, 'gray-light');
        }
        &:first-child {
            border-radius: 8px 0 0 8px;
        }
        &:last-child {
            border-radius: 0 8px 8px 0;
        }
    }
    &--disabled {
        pointer-events: none;
        .option:not(.option--selected) {
            color: map-get($colors, 'gray-dark');
        }
    }
}
</style>