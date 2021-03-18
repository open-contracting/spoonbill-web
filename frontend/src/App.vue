<template>
    <v-app>
        <layout-header />

        <v-main>
            <v-container>
                <h1>OCDS Flatten Tool</h1>
                <h4 class="mb-15">Convert your OCDS JSON data into Excel</h4>
                <router-view />
            </v-container>
        </v-main>
    </v-app>
</template>

<script>
import LayoutHeader from './components/Layout/LayoutHeader';

export default {
    name: 'App',

    components: {
        LayoutHeader,
    },

    data: () => ({
        //
    }),
};
</script>
