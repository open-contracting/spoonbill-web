<template>
    <v-row>
        <v-col cols="12">
            <translate tag="h2" class="page-title">Download your tables</translate>

            <div class="mt-9 download-options justify-center justify-md-start">
                <div class="download-option">
                    <app-button text color="darkest" :disabled="!selections" @click="createFlatten(EXPORT_FORMATS.XLSX)">
                        <translate>Generate as a multi sheet XLSX</translate>
                    </app-button>
                    <div class="mt-7 download-block" :class="xlsxFlattenClasses">
                        <div class="rounded-box">
                            <v-img max-height="60" contain src="@/assets/icons/xls.svg" />
                            <v-btn class="mt-6" large color="gray-light" @click="download(EXPORT_FORMATS.XLSX)">
                                <translate>Download</translate>
                            </v-btn>
                        </div>
                        <div class="d-flex align-center justify-center spin-loader" v-if="xlsxFlattenClasses.processing">
                            <v-img max-width="40" src="@/assets/icons/loader.svg" />
                        </div>
                    </div>
                </div>
                <div class="download-option">
                    <app-button text color="darkest" :disabled="!selections" @click="createFlatten(EXPORT_FORMATS.CSV)">
                        <translate>Generate tables as individual CSV files</translate>
                    </app-button>
                    <div class="mt-7 download-block" :class="csvFlattenClasses">
                        <div class="rounded-box">
                            <v-img max-height="60" contain src="@/assets/icons/csv.svg" />
                            <v-btn class="mt-6" large color="gray-light" @click="download(EXPORT_FORMATS.CSV)">
                                <translate>Download</translate>
                            </v-btn>
                        </div>
                        <div class="d-flex align-center justify-center spin-loader" v-if="csvFlattenClasses.processing">
                            <v-img max-width="40" src="@/assets/icons/loader.svg" />
                        </div>
                    </div>
                </div>
            </div>
        </v-col>
        <v-col class="mt-6 additional-resources" cols="12" md="8" lg="6">
            <translate class="additional-resources__title" tag="h3">Additional resources</translate>
            <translate class="mt-4 mb-3" tag="p">Analysing your data</translate>
            <p class="fw-300">
                <translate>Using the</translate>
                <translate
                    class="ml-1 text-link"
                    tag="a"
                    href="https://standard.open-contracting.org/latest/en/schema/release/"
                    target="_blank"
                    rel="noopener"
                >
                    release schema
                </translate>
                <translate>
                    will further help to understand what the data in the OCDS fields means and how the tables are related.
                </translate>
            </p>
        </v-col>
    </v-row>
</template>

<script>
import AppButton from '@/components/App/AppButton';
import { EXPORT_FORMATS, FLATTEN_STATUSES } from '@/constants';
import ApiService from '@/services/ApiService';
import selectionsMixin from '@/mixins/selectionsMixin';

export default {
    name: 'Download',

    components: { AppButton },

    mixins: [selectionsMixin],

    data() {
        return {
            EXPORT_FORMATS,
        };
    },

    computed: {
        flattens() {
            return this.$store.state.selections?.flattens;
        },

        xlsxFlattenClasses() {
            if (!this.flattens) return false;
            const flatten = this.flattens.find((f) => f.export_format === EXPORT_FORMATS.XLSX) || {};
            return {
                completed: flatten.status === FLATTEN_STATUSES.COMPLETED,
                processing: flatten.status === FLATTEN_STATUSES.PROCESSING,
            };
        },

        csvFlattenClasses() {
            if (!this.flattens) return false;
            const flatten = this.flattens.find((f) => f.export_format === EXPORT_FORMATS.CSV) || {};
            return {
                completed: flatten.status === FLATTEN_STATUSES.COMPLETED,
                processing: flatten.status === FLATTEN_STATUSES.PROCESSING,
            };
        },
    },

    watch: {
        flattens(v) {
            const allCompleted = v && v.every((flatten) => flatten.status === FLATTEN_STATUSES.COMPLETED);
            if (allCompleted) {
                this.$store.dispatch('closeConnection');
            }
        },
    },

    async created() {
        await this.getSelections();
    },

    methods: {
        /**
         * Create flatten
         * @param { 'csv' | 'xlsx' } format - export format
         */
        async createFlatten(format) {
            try {
                const { uploadDetails, selections } = this.$store.state;

                await ApiService.createFlatten(uploadDetails.type + 's', uploadDetails.id, selections.id, format);

                if (this.$store.state.connection) {
                    await this.$store.dispatch('fetchSelections', this.selections.id);
                } else {
                    await this.$store.dispatch('setupConnection', {
                        id: this.$store.state.uploadDetails.id,
                        type: this.$store.state.uploadDetails.type,
                        onOpen: () => this.$store.dispatch('fetchSelections', this.selections.id),
                    });
                }
            } catch (e) {
                console.error(e);
                this.$store.commit('openSnackbar', {
                    text: e.response.data.detail,
                    color: 'error',
                });
            }
        },

        /**
         * Create flatten
         * @param { 'csv' | 'xlsx' } format - export format
         */
        async download(format) {
            const flatten = this.flattens.find((f) => f.export_format === format);
            window.open(flatten.file);
        },
    },
};
</script>

<style scoped lang="scss">
.download-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, 360px);
    column-gap: 36px;
    row-gap: 36px;
    .download-block {
        position: relative;
        pointer-events: none;
        &.completed:not(.processing) .rounded-box {
            opacity: 1;
            pointer-events: auto;
        }
    }
    .rounded-box {
        background-color: #fff;
        margin: 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        border: 1px solid map-get($colors, 'gray-dark');
        width: 257px;
        height: 199px;
        opacity: 0.2;
    }
}
.additional-resources {
    &__title {
        font-size: 20px;
    }
    .fw-300 {
        line-height: 24px;
    }
}
</style>
