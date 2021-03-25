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

    data: () => ({
        //
    }),
};
</script>
<style lang="scss">
@import 'src/assets/styles/main';
</style>
