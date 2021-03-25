<template>
    <v-container>
        <v-row class="pt-6 pb-8">
            <v-col cols="12" md="8" xl="8">
                <layout-info />
                <h2 class="page-title">Select data to flatten to Excel/CSV</h2>

                <p class="page-description">
                    Data you selected needs to be converted into an Excel/CSV file. The Flatten tool converts JSON OCDS data
                    to Excel Excel (.xlsx) and helps users to understand what data is contained in the file.
                </p>

                <p class="page-description">
                    The file size is very large and has multiple tables. It is recommended that you only flatten data that
                    you actually want to use.
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

                <select-data-options class="mt-9" @select="onOptionSelect" />
            </v-col>
            <v-col cols="12" md="4" xl="3" offset-xl="1">
                <select-data-f-a-q class="mt-10" />
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import SelectDataOptions from '@/components/SelectData/SelectDataOptions';
import LayoutInfo from '@/components/Layout/LayoutInfo';
import SelectDataFAQ from '@/components/SelectData/SelectDataFAQ';

export default {
    name: 'SelectData',

    components: { SelectDataFAQ, LayoutInfo, SelectDataOptions },

    methods: {
        /**
         * Handle option select
         * @param { string } option
         */
        onOptionSelect(option) {
            if (option === 'MANUAL') {
                this.$router.push('/select-data/select-file');
            }
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
