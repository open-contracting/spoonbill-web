<template>
    <div class="d-flex flex-column justify-center align-center app-dropzone" @drop="dropHandler" @dragover.prevent>
        <div v-show="loading">
            <v-img height="60" contain src="@/assets/icons/json.svg" />
            <div class="file-name">{{ file && file.name }}</div>
        </div>
        <v-img v-show="!loading" src="@/assets/icons/drag-n-drop.svg" />

        <template v-if="loading">
            <span class="my-3">Upload in progress</span>

            <v-progress-linear height="9" indeterminate color="accent" />

            <v-btn class="app-btn" large @click="cancelRequest" color="gray-light">Cancel</v-btn>
        </template>

        <template v-else>
            <span class="my-7">Drag and drop or click here</span>

            <input type="file" class="d-none" ref="fileInput" @change="onFileSelect" />

            <app-button class="app-btn" large show-icon @click="$refs.fileInput.click()" color="gray-light">
                Browse files
            </app-button>
        </template>
    </div>
</template>

<script>
import AppButton from '@/components/App/AppButton';
import ApiService from '@/services/ApiService';
import axios from 'axios';

export default {
    name: 'AppDropzone',

    components: { AppButton },

    data() {
        return {
            loading: false,
            file: null,
            cancelTokenSource: null,
        };
    },

    methods: {
        /**
         * Handle file select
         * @param { InputEvent } ev
         */
        onFileSelect(ev) {
            if (ev.target.files) {
                this.sendFile(ev.target.files[0]);
                ev.target.value = null;
            }
        },

        /**
         * Handle file drop
         * @param { DragEvent } ev
         */
        dropHandler(ev) {
            ev.preventDefault();
            this.highlighted = false;

            if (ev.dataTransfer?.files?.length) {
                this.sendFile(ev.dataTransfer.files[0]);
            }
        },

        /**
         * Send file; Emits 'send' event on successful submission
         * @param { File } file
         */
        async sendFile(file) {
            if (!this.validateFile(file)) return;

            try {
                this.file = file;
                this.loading = true;
                this.cancelTokenSource = axios.CancelToken.source();
                const formData = new FormData();
                formData.append('file', file);
                const { data } = await ApiService.sendFile(formData, this.cancelTokenSource.token);
                this.$store.commit('openSnackbar', {
                    color: 'success',
                    text: 'File was uploaded. ID: ' + data.id,
                });
                this.$emit('send', data);
            } catch (e) {
                console.error(e);
                if (e.response?.data?.detail) {
                    this.$store.commit('openSnackbar', {
                        color: 'error',
                        text: e.response.data.detail,
                    });
                }
            } finally {
                this.loading = false;
                this.file = null;
                this.cancelTokenSource = null;
            }
        },

        /**
         * Cancel file sending
         */
        cancelRequest() {
            this.cancelTokenSource.cancel('Canceled by user');
            this.$store.commit('openSnackbar', {
                color: 'error',
                text: 'Canceled by user',
            });
        },

        /**
         * Checks file's size and type
         * @param { File } file
         * @return { boolean }
         */
        validateFile(file) {
            if (file.size > 100000000) {
                this.$store.commit('openSnackbar', {
                    color: 'error',
                    text: 'The maximum filesize permitted is 100MB',
                });
                return false;
            }
            return true;
        },
    },
};
</script>

<style scoped lang="scss">
.app-dropzone {
    padding: 52px;
    width: 100%;
    border: 1px dashed map-get($colors, 'gray-dark');
    border-radius: 8px;
    background-color: #ffffff;
    position: relative;
    .file-name {
        margin-top: 5px;
        font-size: 14px;
        font-weight: 300;
    }

    .v-progress-linear {
        margin-bottom: 23px;
        max-width: 375px;
    }
}
</style>
