<template>
    <div class="table">
        <v-row>
            <v-col cols="12" md="6">
                <div v-if="aboutThisTable">
                    <translate tag="p" class="mb-2">About this table</translate>
                    <p class="fw-300" v-for="(item, idx) in aboutThisTable" :key="idx">{{ item }}</p>
                </div>
            </v-col>

            <v-col cols="12" md="6">
                <div class="table-info">
                    <div v-if="availableData.length">
                        <translate tag="p" class="mb-2">Available data</translate>
                        <ul class="app-list">
                            <li v-for="(item, idx) of availableData" :key="idx">{{ item }}</li>
                        </ul>
                    </div>

                    <div class="mt-4" v-if="arrays.length">
                        <translate tag="p" class="mb-2">Arrays</translate>
                        <ul class="app-list">
                            <li v-for="(item, idx) of arrays" :key="idx">{{ item }}</li>
                        </ul>
                    </div>
                </div>
            </v-col>
        </v-row>
        <v-switch
            v-model="isSplit"
            v-if="canBeSplit"
            inset
            hide-details
            color="darkest"
            slot="actions"
            :label="isSplit ? $gettext('Keep arrays in main table') : $gettext('Split arrays into separate tables')"
        ></v-switch>
        <v-skeleton-loader class="mt-8" v-if="loading" type="table-tbody"></v-skeleton-loader>
        <div class="mt-8 tables">
            <app-table
                v-for="(table, idx) in tables"
                :key="table.name"
                :headers="table.headers"
                :name="table.heading || table.name"
                :data="table.data"
                :include="table.include"
                :allow-actions="idx !== 0"
                :additional-columns="additionalColumns"
                @remove="changeIncludeStatus(table, false)"
                @restore="changeIncludeStatus(table, true)"
            />
        </div>
        <div class="mt-15 d-flex">
            <v-btn class="mr-6" color="gray-light" x-large @click="$emit('back')" v-if="isSplit" key="back">
                <translate>Go back</translate>
            </v-btn>

            <v-btn class="mr-6" color="accent" x-large @click="$emit('remove')" v-else key="remove">
                <v-img class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                <translate>Remove table</translate>
            </v-btn>

            <v-btn color="accent" x-large @click="$emit('save')">
                <v-img class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                <translate>Save and Continue</translate>
            </v-btn>
        </div>
    </div>
</template>

<script>
import ApiService from '@/services/ApiService';
import Papa from 'papaparse';
import AppTable from '@/components/App/AppTable';

export default {
    name: 'CustomizeTablesTable',

    components: { AppTable },

    props: {
        table: {
            type: Object,
            required: true,
        },
    },

    data() {
        return {
            loading: false,
            tables: [],
        };
    },

    computed: {
        additionalInfo() {
            return this.$store.state.uploadDetails.available_tables.find((table) => table.name === this.table.name);
        },

        canBeSplit() {
            return this.additionalInfo.arrays?.above_threshold;
        },

        isSplit: {
            get() {
                return this.$store.state.selections.tables.find((table) => table.id === this.table.id).split;
            },
            async set() {
                await this.onSplitSwitchChange();
            },
        },

        aboutThisTable() {
            const name = this.table.name;
            switch (name) {
                case 'awards':
                    return [
                        this.$gettext('This table contains information from the award phase of the contracting process.'),
                        this.$gettext(
                            'There can be more than one award per contracting process e.g. because the ' +
                                'contract is split among different providers, or because it is a standing offer.'
                        ),
                    ];
                case 'parties':
                    return [
                        this.$gettext(
                            'This table contains information on the parties (organizations, economic ' +
                                'operators and other participants) who are involved in the contracting process ' +
                                'and their roles, e.g. buyer, procuring entity, supplier, etc.'
                        ),
                        this.$gettext(
                            'Organization references elsewhere in the data refer back to the entries in this list.'
                        ),
                    ];
                case 'planning':
                    return [
                        this.$gettext('This table contains information from the planning phase of the contracting process.'),
                        this.$gettext(
                            'This includes information related to the process of deciding what to contract, when, and how.'
                        ),
                    ];
                case 'tenders':
                    return [
                        this.$gettext(
                            'This table contains information on the activities undertaken in order ' +
                                'to enter into a contract.'
                        ),
                        this.$gettext(
                            'Data regarding tender process - publicly inviting prospective contractors ' +
                                'to submit bids for evaluation and selecting a winner or winners.'
                        ),
                    ];
                case 'contracts':
                    return [
                        this.$gettext(
                            'This table contains information from the contract creation phase of the ' +
                                'procurement process and the signed contract between the buyer or procuring ' +
                                'entity and supplier(s).'
                        ),
                    ];
                case 'milestones':
                    return [
                        this.$gettext(
                            'This table contains a list of milestones associated with the different stages ' +
                                'of the procurement process (planning, tender, award, contract, implementation).'
                        ),
                    ];
                case 'amendments':
                    return [
                        this.$gettext(
                            'This table contains information on the changes to the different stages of ' +
                                'the procurement process (tender, award, contract). For example, ' +
                                'when the value or duration of a contract is changed. '
                        ),
                        this.$gettext(
                            'The term amendment often has a specific legal ' +
                                'meaning for a publisher. Certain changes to a tender, award, or contract ' +
                                'might only be allowed as part of an amendment.'
                        ),
                    ];
                case 'Documents':
                    return [
                        this.$gettext(
                            'This table contains information on the documents available for the different ' +
                                'stages of the procurement process (planning, tender, award, contract, implementation).'
                        ),
                    ];
                default:
                    return null;
            }
        },

        arrays() {
            const res = [];
            const belowThreshold = this.additionalInfo.arrays?.below_threshold;
            if (belowThreshold) {
                let translated = this.$ngettext(
                    'There is %{ n } array with',
                    'There are %{ n } arrays with',
                    belowThreshold.length
                );
                let belowThresholdString = this.$gettextInterpolate(translated, { n: belowThreshold.length }) + ' ';
                translated = this.$ngettext(
                    '%{ n } item or fewer',
                    '%{ n } items or fewer',
                    this.additionalInfo.arrays.threshold
                );
                belowThresholdString += this.$gettextInterpolate(translated, { n: this.additionalInfo.arrays.threshold });
                res.push(belowThresholdString + ` (${belowThreshold.join(', ')})`);
            }
            const aboveThreshold = this.additionalInfo.arrays?.above_threshold;
            if (aboveThreshold) {
                let translated = this.$ngettext(
                    'There is %{ n } array with more than',
                    'There are %{ n } arrays with more than',
                    aboveThreshold.length
                );
                let aboveThresholdString = this.$gettextInterpolate(translated, { n: aboveThreshold.length }) + ' ';
                translated = this.$ngettext('%{ n } item ', '%{ n } items ', this.additionalInfo.arrays.threshold);
                aboveThresholdString += this.$gettextInterpolate(translated, { n: this.additionalInfo.arrays.threshold });
                res.push(
                    aboveThresholdString +
                        ` (${aboveThreshold.join(', ')}). ` +
                        this.$gettext('This can be split into a separate table to make the data easier to work with')
                );
            }
            return res;
        },

        additionalColumns() {
            return this.additionalInfo.available_data?.columns?.additional || [];
        },

        availableData() {
            const res = [];
            const availableColumns = this.additionalInfo.available_data?.columns?.available;
            if (availableColumns) {
                let translated = this.$ngettext(
                    'There is data for %{ n } column',
                    'There are data for %{ n } of columns',
                    availableColumns
                );
                res.push(this.$gettextInterpolate(translated, { n: availableColumns }));
            }
            const additionalColumns = this.additionalInfo.available_data?.columns?.additional;
            if (additionalColumns?.length) {
                let translated = this.$ngettext(
                    'There is %{ n } column with additional data not part of OCDS',
                    'There are %{ n } columns with additional data not part of OCDS',
                    additionalColumns
                );
                res.push(this.$gettextInterpolate(translated, { n: additionalColumns }));
                res.push(
                    additionalColumns.length === 1
                        ? this.$gettext('This column is highlighted in violet')
                        : this.$gettext('These columns are highlighted in violet')
                );
            }
            return res;
        },
    },

    watch: {
        table: {
            handler(v) {
                this.getTablePreview(v.id);
            },
            immediate: true,
        },
    },

    methods: {
        async onSplitSwitchChange() {
            try {
                await this.$store.dispatch('updateSplitStatus', {
                    tableId: this.table.id,
                    value: !this.isSplit,
                });
                await this.getTablePreview(this.table.id);
            } catch (e) {
                /* istanbul ignore next */
                console.error(e);
            }
        },

        /**
         * Fetch and parse preview of table
         * @param { string } tableId
         */
        async getTablePreview(tableId) {
            window.scroll(0, 0);
            this.loading = true;
            const { uploadDetails, selections } = this.$store.state;
            const { data } = await ApiService.getTablePreview(
                uploadDetails.type + 's',
                uploadDetails.id,
                selections.id,
                tableId
            );
            this.tables = await Promise.all(
                data.map(async (preview) => {
                    const parsed = await Papa.parse(data[0].preview, {
                        skipEmptyLines: true,
                    });
                    return {
                        id: preview.id,
                        name: preview.name,
                        heading: preview.heading,
                        headers: parsed.data[0],
                        data: parsed.data.slice(1),
                        include: true,
                    };
                })
            );
            this.loading = false;
        },

        /**
         * Change include status of table
         * @param { { include: boolean, id: string } } table
         * @param { boolean } value
         */
        async changeIncludeStatus(table, value) {
            try {
                await ApiService.changeIncludeStatus(
                    this.$store.state.uploadDetails.type + 's',
                    this.$store.state.uploadDetails.id,
                    this.$store.state.selections.id,
                    table.id,
                    value
                );
                table.include = value;
            } catch (e) {
                /* istanbul ignore next */
                console.error(e);
            }
        },
    },
};
</script>

<style scoped lang="scss">
.table {
    &__name {
        text-transform: capitalize;
        font-size: 20px;
        color: map-get($colors, 'primary');
    }
    .block-content {
        font-weight: 300;
    }
}
.tables {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}
</style>
