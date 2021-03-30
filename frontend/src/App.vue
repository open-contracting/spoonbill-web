<template>
    <v-app>
        <layout-header />

        <v-main>
            <v-container class="pt-15 pb-5">
                <router-view />
            </v-container>
        </v-main>

        <v-snackbar v-model="snackbar.opened" :timeout="10000" :color="snackbar.color" right top>
            <v-icon class="mr-2">
                {{ snackbar.color === 'error' ? 'mdi-alert-circle-outline' : 'mdi-check-circle-outline' }}
            </v-icon>

            <span class="text-light-14">{{ snackbar.text }}</span>

            <template v-slot:action="{ attrs }">
                <v-btn icon v-bind="attrs" @click="$store.commit('closeSnackbar')">
                    <v-icon color="white">mdi-close</v-icon>
                </v-btn>
            </template>
        </v-snackbar>
    </v-app>
</template>

<script>
import LayoutHeader from './components/Layout/LayoutHeader';
import getQueryParam from '@/utils/getQueryParam';
import { UPLOAD_TYPES, UPLOAD_STATUSES } from '@/constants';

export default {
    name: 'App',

    components: { LayoutHeader },

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
        const fileId = getQueryParam('file');
        if (urlId || fileId) {
            const type = urlId ? UPLOAD_TYPES.URL : UPLOAD_TYPES.FILE;
            await this.$store.dispatch('fetchUploadDetails', {
                id: urlId || fileId,
                type,
            });
            const uploadDetails = this.$store.state.uploadDetails;
            if (!uploadDetails) {
                this.$router.push('/upload-file').catch(() => {});
                return;
            }
            this.$store.commit('increaseNumberOfUploads');
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
        } else {
            this.$router.push('/upload-file').catch(() => {});
        }
    },
};
</script>
<style lang="scss">
@import 'src/assets/styles/main';
</style>
