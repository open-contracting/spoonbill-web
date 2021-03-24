<template>
    <v-app>
        <layout-header />

        <v-main>
            <v-container>
                <v-row>
                    <v-col cols="12" md="8" xl="9">
                        <h1>OCDS Flatten Tool</h1>
                        <p class="mb-15">Convert your OCDS JSON data into Excel</p>
                        <router-view />
                    </v-col>
                    <v-col cols="12" md="4" xl="3">
                        <FAQ class="mt-10" />
                    </v-col>
                </v-row>
            </v-container>
        </v-main>
    </v-app>
</template>

<script>
import LayoutHeader from './components/Layout/LayoutHeader';
import FAQ from '@/components/Layout/FAQ';

export default {
    name: 'App',

    components: {
        FAQ,
        LayoutHeader,
    },

    data: () => ({
        //
    }),
};
</script>
