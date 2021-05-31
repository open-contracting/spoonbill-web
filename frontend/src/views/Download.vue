<template>
    <v-row>
        <v-col cols="12">
            <translate :key="heading" tag="h2" class="page-title">{{ heading }}</translate>

            <div class="mt-7 download-options justify-center justify-md-start">
                <div class="download-option">
                    <div class="download-block" :class="xlsxFlattenClasses">
                        <div class="rounded-box">
                            <v-img max-height="60" contain src="@/assets/icons/xls.svg" />
                            <v-btn
                                v-if="xlsxFlattenClasses.completed"
                                key="downloadXls"
                                class="mt-6"
                                large
                                color="accent"
                                @click="download(EXPORT_FORMATS.XLSX)"
                            >
                                <translate>Download XLSX</translate>
                            </v-btn>
                            <v-btn
                                v-else
                                key="generateXls"
                                :disabled="!selections"
                                class="mt-6"
                                large
                                color="accent"
                                @click="generateFile(EXPORT_FORMATS.XLSX)"
                            >
                                <translate>Generate XLSX</translate>
                            </v-btn>
                        </div>
                        <div class="d-flex align-center justify-center spin-loader" v-if="xlsxFlattenClasses.processing">
                            <v-img max-width="40" src="@/assets/icons/loader.svg" />
                        </div>
                    </div>
                </div>
                <div class="download-option">
                    <div class="download-block" :class="csvFlattenClasses">
                        <div class="rounded-box">
                            <v-img max-height="60" contain src="@/assets/icons/csv.svg" />
                            <v-btn
                                v-if="csvFlattenClasses.completed"
                                key="downloadCsv"
                                class="mt-6"
                                large
                                color="accent"
                                @click="download(EXPORT_FORMATS.CSV)"
                            >
                                <translate>Download CSV</translate>
                            </v-btn>
                            <v-btn
                                v-else
                                :disabled="!selections"
                                key="generateCsv"
                                class="mt-6"
                                large
                                color="accent"
                                @click="generateFile(EXPORT_FORMATS.CSV)"
                            >
                                <translate>Generate CSV</translate>
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
            <ul class="app-list">
                <li>
                    <translate>You can find a full list of definitions of the different OCDS fields in the</translate>
                    <translate
                        class="text-link"
                        tag="a"
                        href="https://standard.open-contracting.org/latest/en/schema/release/"
                        target="_blank"
                        rel="noopener"
                    >
                        release schema
                    </translate>
                    <translate>or using the</translate>
                    <translate
                        class="text-link"
                        tag="a"
                        href="https://open-contracting.github.io/ocds-r-manual/#introduction"
                        target="_blank"
                        rel="noopener"
                    >
                        OCDS Glossary</translate
                    >.
                </li>
                <li class="my-3">
                    <translate>You can learn more about how to analyse your Excel data using the following</translate>
                    <translate
                        class="text-link"
                        tag="a"
                        href="https://open-contracting.org/learn/use#analyze"
                        target="_blank"
                        rel="noopener"
                    >
                        video tutorials</translate
                    >.
                </li>
                <li>
                    <translate>
                        If you are experienced with R, our manual for how to use R to analyse OCDS data can be found
                    </translate>
                    <translate
                        class="text-link"
                        tag="a"
                        href="https://open-contracting.github.io/ocds-r-manual/#introduction"
                        target="_blank"
                        rel="noopener"
                    >
                        here</translate
                    >.
                </li>
            </ul>
        </v-col>
    </v-row>
</template>

<script>
import { EXPORT_FORMATS, FLATTEN_STATUSES } from '@/constants';
import ApiService from '@/services/ApiService';
import selectionsMixin from '@/mixins/selectionsMixin';

export default {
    name: 'Download',

    mixins: [selectionsMixin],

    data() {
        return {
            EXPORT_FORMATS,
            completed: [],
        };
    },

    computed: {
        heading() {
            let text = 'Select how to generate your tables';
            if (this.lastGeneratedFormat === this.EXPORT_FORMATS.XLSX) {
                text = 'Download your XLSX';
            } else if (this.lastGeneratedFormat === this.EXPORT_FORMATS.CSV) {
                text = 'Download your CSV';
            }
            return text;
        },
        flattens() {
            return this.$store.state.selections?.flattens;
        },

        lastGeneratedFormat() {
            return this.completed.length && this.completed[this.completed.length - 1];
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
            if (v) {
                v.forEach((flatten) => {
                    if (!this.completed.includes(flatten.export_format) && flatten.status === FLATTEN_STATUSES.COMPLETED) {
                        this.completed.push(flatten.export_format);
                    }
                });
            }
            const allCompleted =
                v && v.every((flatten) => [FLATTEN_STATUSES.COMPLETED, FLATTEN_STATUSES.FAILED].includes(flatten.status));
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
         * Generate file
         * @param { 'csv' | 'xlsx' } format - export format
         */
        generateFile(format) {
            const flatten = this.flattens && this.flattens.find((f) => f.export_format === format);
            if (flatten) {
                if ([FLATTEN_STATUSES.FAILED, FLATTEN_STATUSES.COMPLETED].includes(flatten.status)) {
                    this.scheduleFlattenGeneration(flatten.id);
                }
            } else {
                this.createFlatten(format);
            }
        },

        /**
         * Schedule flatten generation
         * @param { string } id - flatten id
         */
        async scheduleFlattenGeneration(id) {
            try {
                const { uploadDetails, selections } = this.$store.state;

                await ApiService.scheduleFlattenGeneration(uploadDetails.type + 's', uploadDetails.id, selections.id, id);

                await this.subscribeOnChanges();
            } catch (e) {
                /* istanbul ignore next */
                this.$error(e);
            }
        },

        async subscribeOnChanges() {
            if (this.$store.state.connection) {
                await this.$store.dispatch('fetchSelections', this.selections.id);
            } else {
                await this.$store.dispatch('setupConnection', {
                    id: this.$store.state.uploadDetails.id,
                    type: this.$store.state.uploadDetails.type,
                    onOpen: () => this.$store.dispatch('fetchSelections', this.selections.id),
                });
            }
        },

        /**
         * Create flatten
         * @param { 'csv' | 'xlsx' } format - export format
         */
        async createFlatten(format) {
            try {
                const { uploadDetails, selections } = this.$store.state;

                await ApiService.createFlatten(uploadDetails.type + 's', uploadDetails.id, selections.id, format);

                await this.subscribeOnChanges();
            } catch (e) {
                /* istanbul ignore next */
                this.$error(e);
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
        &.processing:not(.completed) .rounded-box {
            opacity: 0.2;
            pointer-events: none;
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
