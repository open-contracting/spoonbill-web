<template>
    <v-row>
        <v-col cols="12" md="8" xl="8">
            <layout-info />
            <h2 class="page-title">Select a JSON file to flatten</h2>

            <p class="page-description">
                The Flatten tool converts JSON OCDS data to Excel (.xlsx) and helps users to understand what data is
                contained in the file.
            </p>

            <p class="page-description">
                The file size is very large and has multiple tables. It is recommended that you only flatten data that you
                actually want to use.
            </p>

            <upload-file-input class="mt-7" />
        </v-col>
        <v-col cols="12" md="4" xl="3" offset-xl="1">
            <upload-file-f-a-q accent class="mt-5" />
        </v-col>
    </v-row>
</template>

<script>
import UploadFileInput from '@/components/UploadFile/UploadFileInput';
import LayoutInfo from '@/components/Layout/LayoutInfo';
import UploadFileFAQ from '@/components/UploadFile/UploadFileFAQ';

export default {
    name: 'UploadFile',

    components: { UploadFileFAQ, UploadFileInput, LayoutInfo },
};
</script>

<style scoped lang="scss"></style>
