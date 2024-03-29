<template>
    <v-app>
        <layout-header />

        <v-main>
            <v-container class="pt-12 pb-5">
                <v-overlay v-if="loading" class="d-flex align-center justify-center" :value="true">
                    <v-progress-circular size="48" color="accent" indeterminate />
                </v-overlay>

                <template v-else>
                    <layout-info />
                    <router-view />
                </template>
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
import { UPLOAD_TYPES } from '@/constants';
import AppConfirmDialog from '@/components/App/AppConfirmDialog';
import LayoutInfo from '@/components/Layout/LayoutInfo';
import axios from 'axios';

export default {
    name: 'App',

    components: { LayoutInfo, AppConfirmDialog, LayoutHeader },

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
        lang() {
            return this.$language.current;
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
                            onOpen: () => this.$store.dispatch('fetchUploadDetails', { id: v.id, type: v.type }),
                        });
                } else {
                    this.$store.dispatch('closeConnection');
                }
            },
            immediate: true,
        },
        lang: {
            handler(val) {
                localStorage && localStorage.setItem('lang', val);
                axios.defaults.headers.common['Accept-Language'] = val;
                this.updateLangQueryParam(val);
            },
        },
    },

    async created() {
        const urlId = getQueryParam('url');
        const uploadId = getQueryParam('upload');
        const query = {
            lang: this.lang,
        };
        if (urlId || uploadId) {
            this.loading = true;
            const type = urlId ? UPLOAD_TYPES.URL : UPLOAD_TYPES.UPLOAD;
            await this.$store.dispatch('fetchUploadDetails', {
                id: urlId || uploadId,
                type,
            });
            const uploadDetails = this.$store.state.uploadDetails;
            if (!uploadDetails) {
                this.$router
                    .push({
                        name: 'upload file',
                        params: {
                            forced: 'true',
                        },
                        query,
                    })
                    .catch(() => {});
                this.loading = false;
                return;
            }
            this.loading = false;
            this.$store.commit('increaseNumberOfUploads');
        } else {
            this.$router
                .push({
                    name: 'upload file',
                    params: {
                        forced: 'true',
                    },
                    query,
                })
                .catch(() => {});
        }
    },
    methods: {
        updateLangQueryParam(lang) {
            this.$router.push({
                path: this.$route.path,
                query: {
                    ...this.$route.query,
                    lang,
                },
            });
        },
    },
};
</script>
<style lang="scss">
@import 'src/assets/styles/main';
</style>
