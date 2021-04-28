<template>
    <v-row>
        <v-col cols="12" md="8">
            <translate tag="h2" class="page-title">Select data to flatten to Excel/CSV</translate>

            <translate tag="p" class="page-description">
                Data you selected needs to be converted into an Excel/CSV file. The Flatten tool converts JSON OCDS data to
                Excel Excel (.xlsx) and helps users to understand what data is contained in the file.
            </translate>

            <translate tag="p" class="page-description">
                The file size is very large and has multiple tables. It is recommended that you only flatten data that you
                actually want to use.
            </translate>

            <v-container>
                <v-row class="mt-7 rounded-box defaults">
                    <v-col cols="4">
                        <translate class="defaults__title">Data for country:</translate>
                        <span class="defaults__value">United Kingdom</span>
                    </v-col>
                    <v-col cols="4">
                        <translate class="defaults__title">Data for range:</translate>
                        <span class="defaults__value">Last 6 month</span>
                    </v-col>
                    <v-col cols="4">
                        <translate class="defaults__title">Data from:</translate>
                        <span class="defaults__value">OCP Kingfisher database</span>
                    </v-col>
                </v-row>
            </v-container>

            <upload-file-options class="mt-9" />
        </v-col>
        <v-col cols="12" md="4">
            <app-f-a-q>
                <translate slot="title">FAQ</translate>

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
import UploadFileOptions from '@/components/UploadFile/UploadFileOptions';
import AppFAQ from '@/components/App/AppFAQ';

export default {
    name: 'UploadFileRegistry',

    components: { AppFAQ, UploadFileOptions },

    data() {
        return {
            panelsValue: [0],
        };
    },

    computed: {
        faqItems() {
            return [
                {
                    title: this.$gettext('What is OCDS Lite?'),
                    content:
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
                {
                    title: this.$gettext('What is OCDS schema version 1.1?'),
                    content:
                        'Lorem ipsum dolor sit amet, adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
                {
                    title: this.$gettext('What is the data review tool?'),
                    content:
                        'Lorem ipsum dolor sit amet, adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
            ];
        },
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
