<template>
    <v-app>
        <layout-header />

        <v-main>
            <v-container class="pt-15 pb-5">
                <v-overlay v-if="loading" class="d-flex align-center justify-center" :value="true">
                    <v-progress-circular size="48" color="accent" indeterminate />
                </v-overlay>

                <router-view v-else />
            </v-container>
        </v-main>

        <v-snackbar v-model="snackbar.opened" :timeout="5000" :color="snackbar.color" right top>
            <v-icon class="mr-2">
                {{ snackbar.color === 'error' ? 'mdi-alert-circle-outline' : 'mdi-check-circle-outline' }}
            </v-icon>

            <span class="text-light-14 pt-1">{{ snackbar.text }}</span>

            <template v-slot:action="{ attrs }">
                <v-btn icon v-bind="attrs" @click="$store.commit('closeSnackbar')">
                    <v-icon color="white">mdi-close</v-icon>
                </v-btn>
            </template>
        </v-snackbar>

        <app-confirm-dialog />
    </v-app>
</template>

<script>
import LayoutHeader from './components/Layout/LayoutHeader';
import getQueryParam from '@/utils/getQueryParam';
import { UPLOAD_TYPES, UPLOAD_STATUSES } from '@/constants';
import AppConfirmDialog from '@/components/App/AppConfirmDialog';

export default {
    name: 'App',

    components: { AppConfirmDialog, LayoutHeader },

    data() {
        return {
            loading: false,
        };
    },

    computed: {
        snackbar() {
            return this.$store.state.snackbar;
        },

        uploadDetails() {
            return this.$store.state.uploadDetails;
        },
    },

    watch: {
        uploadDetails: {
            handler(v) {
                if (v && typeof v.validation?.is_valid !== 'boolean') {
                    !this.$store.state.connection &&
                        this.$store.dispatch('setupConnection', {
                            id: v.id,
                            type: v.type,
                        });
                } else {
                    this.$store.dispatch('closeConnection');
                }
            },
            immediate: true,
        },
    },

    async created() {
        const urlId = getQueryParam('url');
        const uploadId = getQueryParam('upload');
        const selectionsId = getQueryParam('selections');
        if (urlId || uploadId) {
            this.loading = true;
            const type = urlId ? UPLOAD_TYPES.URL : UPLOAD_TYPES.UPLOAD;
            await this.$store.dispatch('fetchUploadDetails', {
                id: urlId || uploadId,
                type,
            });
            const uploadDetails = this.$store.state.uploadDetails;
            if (!uploadDetails) {
                this.$router.push('/upload-file').catch(() => {});
                this.loading = false;
                return;
            }
            this.$store.commit('increaseNumberOfUploads');
            if (selectionsId) {
                this.$router
                    .push(`/customize-tables?${type.toLowerCase()}=${uploadDetails.id}&selections=${selectionsId}`)
                    .catch(() => {});
                this.loading = false;
                return;
            }
            if (
                [
                    UPLOAD_STATUSES.QUEUED_DOWNLOAD,
                    UPLOAD_STATUSES.DOWNLOADING,
                    UPLOAD_STATUSES.QUEUED_VALIDATION,
                    UPLOAD_STATUSES.VALIDATION,
                ].includes(uploadDetails.status)
            ) {
                this.$router.push(`/upload-file?${type.toLowerCase()}=${uploadDetails.id}`).catch(() => {});
            }
            this.loading = false;
        } else {
            this.$router.push('/upload-file').catch(() => {});
        }
    },
};
</script>
<style lang="scss">
@import 'src/assets/styles/main';
</style>
