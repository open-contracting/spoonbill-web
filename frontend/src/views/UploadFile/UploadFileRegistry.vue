<template>
    <v-row>
        <v-col cols="12" md="8" xl="8">
            <layout-info />
            <h2 class="page-title">Select data to flatten to Excel/CSV</h2>

            <p class="page-description">
                Data you selected needs to be converted into an Excel/CSV file. The Flatten tool converts JSON OCDS data to
                Excel Excel (.xlsx) and helps users to understand what data is contained in the file.
            </p>

            <p class="page-description">
                The file size is very large and has multiple tables. It is recommended that you only flatten data that you
                actually want to use.
            </p>

            <v-container>
                <v-row class="mt-7 rounded-box defaults">
                    <v-col cols="4">
                        <span class="defaults__title">Data for country:</span>
                        <span class="defaults__value">United Kingdom</span>
                    </v-col>
                    <v-col cols="4">
                        <span class="defaults__title">Data for range:</span>
                        <span class="defaults__value">Last 6 month</span>
                    </v-col>
                    <v-col cols="4">
                        <span class="defaults__title">Data from:</span>
                        <span class="defaults__value">OCP Kingfisher database</span>
                    </v-col>
                </v-row>
            </v-container>

            <upload-file-options class="mt-9" />
        </v-col>
        <v-col cols="12" md="4" xl="3" offset-xl="1">
            <upload-file-f-a-q class="mt-5" />
        </v-col>
    </v-row>
</template>

<script>
import LayoutInfo from '@/components/Layout/LayoutInfo';
import UploadFileFAQ from '@/components/UploadFile/UploadFileFAQ';
import UploadFileOptions from '@/components/UploadFile/UploadFileOptions';

export default {
    name: 'UploadFileRegistry',

    components: { UploadFileOptions, UploadFileFAQ, LayoutInfo },
};
</script>

<style scoped lang="scss">
.defaults {
    padding: 12px;
    background-color: map-get($colors, 'gray-light');
    font-size: 14px;
    &__title {
        margin-bottom: 6px;
        color: map-get($colors, 'darkest');
    }
    &__value {
        font-weight: 300;
    }
    .col {
        display: flex;
        flex-direction: column;
    }
}
</style>
