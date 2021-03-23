<template>
    <v-app>
        <layout-header />

        <v-main>
            <v-container class="d-flex justify-space-between">
                <div class="main-block">
                    <h1>OCDS Flatten Tool</h1>
                    <p class="mb-15">Convert your OCDS JSON data into Excel</p>
                    <router-view />
                </div>
                <FAQ class="mt-10" v-if="$vuetify.breakpoint.mdAndUp" />
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
<style scoped lang="scss">
.main-block {
    flex-grow: 1;
}
</style>
