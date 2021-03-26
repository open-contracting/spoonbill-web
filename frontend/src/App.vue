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

export default {
    name: 'App',

    components: { LayoutHeader },

    computed: {
        snackbar() {
            return this.$store.state.snackbar;
        },
    },

    async created() {
        if (window.location.hash.includes('?id=')) {
            const id = window.location.hash.split('=')[1];
            if (id) {
                await this.$store.dispatch('fetchUploadDetails', id);
                if (typeof this.$store.state.uploadDetails?.validation?.is_valid !== 'boolean') {
                    this.$store.dispatch('setupConnection', id);
                }
            }
        } else {
            this.$router.push('/select-data').catch(() => {});
        }
    },
};
</script>
<style lang="scss">
@import 'src/assets/styles/main';
</style>
