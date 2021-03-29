<template>
    <v-app>
        <layout-header />

        <v-main>
            <router-view />
        </v-main>

        <v-snackbar v-model="snackbar.opened" multi-line :color="snackbar.color" right bottom>
            {{ snackbar.text }}

            <template v-slot:action="{ attrs }">
                <v-btn icon v-bind="attrs" @click="$store.commit('closeSnackbar')">
                    <v-icon color="primary">mdi-close</v-icon>
                </v-btn>
            </template>
        </v-snackbar>
    </v-app>
</template>

<script>
import LayoutHeader from './components/Layout/LayoutHeader';
import getQueryParam from '@/utils/getQueryParam';
import { UPLOAD_TYPES } from '@/constants';

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
            await this.$store.dispatch('fetchUploadDetails', {
                id: urlId || fileId,
                type: urlId ? UPLOAD_TYPES.URL : UPLOAD_TYPES.FILE,
            });
        } else {
            this.$router.push('/select-data').catch(() => {});
        }
    },
};
</script>
<style lang="scss">
@import 'src/assets/styles/main';
</style>
