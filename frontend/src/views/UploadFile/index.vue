<template>
    <v-row>
        <v-col cols="12" md="8">
            <translate tag="h2" class="page-title">Select a JSON file to flatten</translate>

            <translate tag="p" class="page-description">
                The Flatten Tool converts JSON OCDS data to Excel (.xlsx) and helps you to understand what data is contained
                in the file.
            </translate>

            <translate tag="p" class="page-description">
                If the file size you have uploaded is very large and has multiple tables, it is recommended that you only
                select and flatten data that you actually want to use.
            </translate>

            <upload-file-input class="mt-7" />
        </v-col>
        <v-col cols="12" md="4">
            <app-f-a-q accent>
                <v-icon slot="title" color="primary">mdi-alert</v-icon>

                <div class="pa-5 pt-0">
                    <p class="mb-0">
                        <translate>If you would like to convert CSV data to JSON, please use the older </translate>
                        <translate
                            tag="a"
                            class="text-link"
                            target="_blank"
                            rel="noopener"
                            href="https://flatten-tool.readthedocs.io/en/latest/usage-ocds/"
                            >Command-Line tool</translate
                        >.
                        <br />
                        <translate>
                            Please note that the Command-Line Tool requires some knowledge of programming and is not-suited
                            to non-technical users.
                        </translate>
                    </p>
                    <v-divider class="my-5" />
                    <p class="mb-0">
                        <translate>
                            The JSON data you upload should be in OCDS 1.1 or 1.0, otherwise it may not be possible to
                            flatten. If you are uncertain whether your data complies with OCDS, use the
                        </translate>
                        <translate
                            tag="a"
                            class="text-link"
                            target="_blank"
                            rel="noopener"
                            href="https://standard.open-contracting.org/review/"
                        >
                            Data Review Tool
                        </translate>
                        <translate> to check first</translate>.
                    </p>
                </div>
            </app-f-a-q>
        </v-col>
    </v-row>
</template>

<script>
import UploadFileInput from '@/components/UploadFile/UploadFileInput';
import AppFAQ from '@/components/App/AppFAQ';

export default {
    name: 'UploadFile',

    components: { AppFAQ, UploadFileInput },
};
</script>

<style scoped lang="scss"></style>
