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
            <app-f-a-q>
                <span slot="title">FAQ</span>

                <v-expansion-panels :value="panelsValue" accordion multiple>
                    <v-expansion-panel v-for="item in faqItems" :key="item.title">
                        <v-expansion-panel-header class="d-flex">
                            {{ item.title }}
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                            {{ item.content }}
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                </v-expansion-panels>
            </app-f-a-q>
        </v-col>
    </v-row>
</template>

<script>
import LayoutInfo from '@/components/Layout/LayoutInfo';
import UploadFileOptions from '@/components/UploadFile/UploadFileOptions';
import AppFAQ from '@/components/App/AppFAQ';

export default {
    name: 'UploadFileRegistry',

    components: { AppFAQ, UploadFileOptions, LayoutInfo },

    data() {
        return {
            panelsValue: [0],
            faqItems: [
                {
                    title: 'What is OCDS Lite?',
                    content:
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
                {
                    title: 'What is OCDS schema version 1.1?',
                    content:
                        'Lorem ipsum dolor sit amet, adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
                {
                    title: 'What is the data review tool?',
                    content:
                        'Lorem ipsum dolor sit amet, adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
            ],
        };
    },
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
