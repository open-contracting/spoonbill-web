<template>
    <v-row>
        <v-col cols="12" md="8" xl="8">
            <layout-info />
            <translate tag="h2" class="page-title">Download your tables</translate>
        </v-col>
    </v-row>
</template>

<script>
import LayoutInfo from '@/components/Layout/LayoutInfo';

export default {
    name: 'Download',

    components: { LayoutInfo },
};
</script>

<style scoped></style>
