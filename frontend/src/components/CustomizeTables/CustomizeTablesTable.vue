<template>
    <div class="table">
        <h3 class="mb-4 table__name">{{ table.name }}</h3>
        <v-row>
            <v-col cols="6">
                <div class="table-info">
                    <div v-if="availableData.length">
                        <p class="mb-2">Available data</p>
                        <ul class="app-list">
                            <li v-for="(item, idx) of availableData" :key="idx">{{ item }}</li>
                        </ul>
                    </div>

                    <div class="mt-4" v-if="arrays.length">
                        <p class="mb-2">Arrays</p>
                        <ul class="app-list">
                            <li v-for="(item, idx) of arrays" :key="idx">{{ item }}</li>
                        </ul>
                    </div>
                </div>
            </v-col>
        </v-row>
        <v-skeleton-loader class="mt-8" v-if="loading" type="table-tbody"></v-skeleton-loader>
        <div class="mt-8 p-relative tables">
            <app-table
                v-for="table in tables"
                :key="table.name"
                :headers="table.headers"
                :name="'Table: ' + table.name"
                :data="table.data"
            />

            <v-switch
                v-model="isSplit"
                inset
                hide-details
                class="mt-0"
                color="darkest"
                slot="actions"
                :label="isSplit ? 'Keep arrays in main table' : 'Split arrays into separate tables'"
                @change="onSplitSwitchChange"
            ></v-switch>
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
                return this.$store.state.selections.tables.find((table) => table.id === this.table.id).splitted;
            },
            async set() {
                await this.onSplitSwitchChange();
            },
        },

        arrays() {
            const res = [];
            const belowThreshold = this.additionalInfo.arrays?.below_threshold;
            if (belowThreshold) {
                const single = belowThreshold.length === 1;
                res.push(`There ${single ? 'is' : 'are'} ${belowThreshold.length} ${single ? 'array' : 'arrays'} with
                ${this.additionalInfo.arrays.threshold} items or fewer (${belowThreshold.join(', ')})`);
            }
            const aboveThreshold = this.additionalInfo.arrays?.above_threshold;
            if (aboveThreshold) {
                const single = aboveThreshold.length === 1;
                res.push(`There ${single ? 'is' : 'are'} ${aboveThreshold.length} ${single ? 'array' : 'arrays'} with
                more than ${this.additionalInfo.arrays.threshold} items (${aboveThreshold.join(', ')}). This can be
                split into a separate table to make the data easier to work with`);
            }
            return res;
        },

        availableData() {
            const res = [];
            const availableColumns = this.additionalInfo.available_data?.columns?.available;
            if (availableColumns) {
                const single = availableColumns.length === 1;
                res.push(`There ${single ? 'is' : 'are'} data for ${availableColumns} of columns`);
            }
            const additionalColumns = this.additionalInfo.available_data?.additional;
            if (additionalColumns) {
                const single = additionalColumns.length === 1;
                res.push(`There ${single ? 'is' : 'are'} ${additionalColumns.length} ${single ? 'column' : 'columns'}
                with additional data not part of OCDS`);
                res.push(`${single ? 'This' : 'These'} ${single ? 'column' : 'columns'} ${single ? 'is' : 'are'}
                highlighted in violet`);
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
                console.error(e);
            }
        },

        async getTablePreview(tableId) {
            this.loading = true;
            const { uploadDetails, selections } = this.$store.state;
            const { data } = await ApiService.getTablePreview(
                uploadDetails.type + 's',
                uploadDetails.id,
                selections.id,
                tableId,
            );
            this.tables = await Promise.all(
                data.map(async (preview) => {
                    const parsed = await Papa.parse(data[0].preview);
                    return {
                        name: preview.name,
                        headers: parsed.data[0],
                        data: parsed.data.slice(1),
                    };
                }),
            );
            this.loading = false;
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
