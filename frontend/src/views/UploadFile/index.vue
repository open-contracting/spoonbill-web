<template>
    <v-row>
        <v-col cols="12" md="8" :key="key">
            <translate tag="h2" class="page-title">Select a JSON file to flatten</translate>
            <translate v-if="canShowDefaultText">
                The Flatten Tool converts JSON OCDS data to Excel (.xlsx) and helps you to understand what data is contained
                in the file.
            </translate>
            <translate tag="p" class="page-description" v-else>
                Data you selected needs to be converted into an Excel/CSV file. The Flatten tool converts JSON OCDS data to
                Excel (.xlsx) and helps users to understand what data is contained in the file.
            </translate>

            <translate tag="p" class="page-description" v-if="canShowDefaultText">
                If the file size you have uploaded is very large and has multiple tables, it is recommended that you only
                select and flatten data that you actually want to use.
            </translate>
            <translate tag="p" class="page-description" v-else>
                The file size is very large and has multiple tables. It is recommended that you only flatten data that you
                actually want to use.
            </translate>
            <upload-file-input class="mt-7" />
        </v-col>
        <v-col cols="12" md="4">
            <app-f-a-q accent>
                <div slot="title" color="primary">FAQ</div>
                <v-expansion-panels :value="panelsValue" accordion multiple>
                    <v-expansion-panel>
                        <v-expansion-panel-header class="d-flex">
                            <translate> How do I convert CSV or Excel data to JSON? </translate>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                            <translate> If you would like to convert CSV data to JSON, please use the older </translate>
                            <span>
                                <a href="https://open-contracting.github.io/spoonbill/" target="_blank">
                                    Command-Line tool.
                                </a>
                            </span>
                            <br />
                            <translate>
                                Please note that the Command-Line Tool requires some knowledge of programming and is not
                                suited to non-technical users.
                            </translate>
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                    <v-expansion-panel>
                        <v-expansion-panel-header class="d-flex">
                            <translate> What should I do if there are issues with my file? </translate>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                            <translate>
                                The JSON data you upload should be in OCDS version 1.1 or 1.0, otherwise it may not be
                                possible to flatten. <br />If you are uncertain whether your data complies with OCDS, use the
                            </translate>

                            <span>
                                <a href="https://standard.open-contracting.org/review/" target="_blank">
                                    Data Review Tool
                                </a>
                            </span>
                            <translate> to check first. </translate>
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                </v-expansion-panels>
            </app-f-a-q>
            <!-- <app-f-a-q accent>
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
            </app-f-a-q> -->
        </v-col>
    </v-row>
</template>

<script>
import UploadFileInput from '@/components/UploadFile/UploadFileInput';
import AppFAQ from '@/components/App/AppFAQ';

export default {
    name: 'UploadFile',
    data: function () {
        return {
            panelsValue: [0],
            key: 0,
        };
    },
    watch: {
        canShowDefaultText() {
            this.key += 1;
        },
    },
    components: { AppFAQ, UploadFileInput },
    computed: {
        canShowDefaultText() {
            if (!this.$store.state.uploadDetails) {
                return true;
            } else {
                if (!this.$store.getters.isFileFromDataRegistry) {
                    return true;
                } else {
                    return false;
                }
            }
        },
    },
};
</script>

<style scoped lang="scss">
br {
    margin-top: 10px;
    content: '';
    display: block;
}
</style>
