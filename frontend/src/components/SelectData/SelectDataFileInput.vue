<template>
    <div>
        <div class="mb-4 d-flex options">
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
            <select-data-loading-progress
                v-if="loading.value"
                :cancelable="loading.cancelable"
                :status="loading.status"
                :file-name="loading.fileName"
                :percent="loading.percent"
                :color="loading.color"
                @cancel="cancelRequest"
            />

            <template v-else>
                <app-dropzone @input="sendFile" v-if="uploadType === 'FILE'" />

                <select-data-url-input @submit="sendUrl" v-else />
            </template>

            <div
                class="d-flex justify-space-between align-center status-update"
                v-for="(update, idx) in updates"
                :style="{ top: idx === 0 ? '8px' : idx * 85 + 8 + 'px' }"
                :class="update.type"
                :key="idx"
            >
                <div class="text-light-14">
                    {{ update.content }}
                </div>
                <v-btn class="ml-5" icon @click="updates.splice(idx, 1)">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </div>
        </div>

        <p v-if="!isValid" class="mt-4 text-light-14">
            Note that large files may take a while to process. Please be patient.
        </p>

        <select-data-options class="mt-15" v-if="isValid" @select="onOptionSelect" />
    </div>
</template>

<script>
import AppDropzone from '@/components/App/AppDropzone';
import SelectDataUrlInput from '@/components/SelectData/SelectDataUrlInput';
import axios from 'axios';
import ApiService from '@/services/ApiService';
import { UPLOAD_STATUSES } from '@/constants';
import SelectDataLoadingProgress from '@/components/SelectData/SelectDataLoadingProgress';
import SelectDataOptions from '@/components/SelectData/SelectDataOptions';

export default {
    name: 'SelectDataFileInput',

    components: { SelectDataOptions, SelectDataLoadingProgress, SelectDataUrlInput, AppDropzone },

    data() {
        return {
            loading: {
                value: false,
                status: null,
                fileName: null,
                cancelable: false,
                percent: 0,
            },
            updates: [],
            cancelTokenSource: null,
            options: [
                {
                    title: 'Upload JSON file',
                    value: 'FILE',
                },
                {
                    title: 'Supply a URL for JSON',
                    value: 'URL',
                },
            ],
            /** @type { 'FILE' | 'URL' }*/
            uploadType: 'FILE',
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
    },

    watch: {
        uploadDetails: {
            handler(v) {
                if (!v) {
                    this.updates = [];
                    return;
                }
                if (v.status === UPLOAD_STATUSES.QUEUED_VALIDATION) {
                    this.loading = {
                        value: true,
                        status: 'File is queued for validation...',
                        fileName: this.fileName || this.$store.state.uploadDetails.id,
                    };
                }
                if (v.status === UPLOAD_STATUSES.VALIDATION) {
                    this.processValidationStatus(v);
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
         * @param { Object } upload - upload details
         */
        processValidationStatus(upload) {
            if (upload.validation.is_valid === false) {
                this.uploadType = 'FILE';
                this.loading.value = false;
                this.updates.push({
                    type: 'error',
                    content:
                        'This file is not compliant with the OCDS schema so cannot be flattened.\n' +
                        'Check your data using the Data Review Tool and resolve the issues before flattening. ',
                });
                return;
            }
            if (upload.validation.is_valid === true) {
                this.uploadType = 'FILE';
                this.loading.value = false;
                this.updates.push({
                    type: 'success',
                    content: 'Now your file is analyzed and ready to use.',
                });
                this.loading = {
                    value: true,
                    percent: 100,
                    status: 'Analysis has been completed',
                    fileName: this.fileName || this.$store.state.uploadDetails.id,
                    color: '#6C75E1',
                };
                this.valid = true;
                return;
            }
            this.loading = {
                value: true,
                percent: 0,
                status: 'File analysis in progress...',
                fileName: this.fileName || this.$store.state.uploadDetails.id,
                color: '#6C75E1',
            };
        },

        /**
         * Send file; Emits 'send' event on successful submission
         * @param { File } file
         */
        async sendFile(file) {
            try {
                this.showLoading(file.name, true);
                this.cancelTokenSource = axios.CancelToken.source();
                const formData = new FormData();
                formData.append('file', file);
                const { data } = await ApiService.sendFile(formData, this.cancelTokenSource.token, (ev) => {
                    this.loading.percent = Math.floor((ev.loaded * 100) / ev.total);
                });
                this.$store.dispatch('setupConnection', data.id);
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
            this.updates = [];
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
                percent: 0,
                status: 'Upload in progress',
                fileName,
                cancelable,
            };
            this.fileName = fileName;
            this.updates = [];
        },

        /**
         * Send url
         * @param { string } url
         */
        async sendUrl(url) {
            try {
                this.showLoading(url, false);
                const { data } = await ApiService.sendUrl(url);
                this.$store.dispatch('setupConnection', data.id);
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
                this.$router.push('/select-data/select-tables/?id=' + this.$store.state.uploadDetails.id);
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
}

.status-update {
    padding: 0 21px;
    position: absolute;
    left: 8px;
    right: 8px;
    z-index: 3;
    height: 80px;
    border-radius: 2px;
    &.success {
        background: #f0f8e5 !important;
        border-left: 8px solid #71b604;
    }
    &.error {
        background: #ffe8e8 !important;
        border-left: 8px solid #ff9393;
    }
}
</style>
