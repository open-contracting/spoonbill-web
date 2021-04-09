<template>
    <div class="table">
        <h3 class="mb-4 table__name">{{ table.name }}</h3>
        <v-row>
            <v-col cols="12" md="8" lg="6">
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

                    <v-switch
                        v-model="isSplit"
                        inset
                        hide-details
                        class="mt-6"
                        color="darkest"
                        slot="actions"
                        :label="
                            isSplit ? $gettext('Keep arrays in main table') : $gettext('Split arrays into separate tables')
                        "
                    ></v-switch>
                </div>
            </v-col>
        </v-row>
        <v-skeleton-loader class="mt-8" v-if="loading" type="table-tbody"></v-skeleton-loader>
        <div class="mt-8 tables">
            <app-table
                v-for="(table, idx) in tables"
                :key="table.name"
                :headers="table.headers"
                :name="'Table: ' + table.name"
                :data="table.data"
                :include="table.include"
                :allow-actions="idx !== 0"
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

        isSplit: {
            get() {
                return this.$store.state.selections.tables.find((table) => table.id === this.table.id).split;
            },
            async set() {
                await this.onSplitSwitchChange();
            },
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
            const additionalColumns = this.additionalInfo.available_data?.additional;
            if (additionalColumns) {
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
                    const parsed = await Papa.parse(data[0].preview);
                    return {
                        id: preview.id,
                        name: preview.name,
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
    .v-input {
        position: absolute;
        right: 0;
        top: -5px;
    }
}
</style>
