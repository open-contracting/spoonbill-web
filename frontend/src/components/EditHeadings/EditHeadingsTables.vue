<template>
    <div>
        <v-skeleton-loader class="mt-8" v-if="loading" type="table-tbody"></v-skeleton-loader>

        <div class="mt-8 tables">
            <app-table
                v-for="table in tables"
                :key="table.id"
                :headers="table.headers"
                :name="table.heading || table.name"
                :data="table.data"
                :include="table.include"
                :additional-columns="additionalColumns"
                editable-name
                @change-name="updateTableHeading($event, table.id)"
                :headings="table.headings"
            />
        </div>
    </div>
</template>

<script>
import ApiService from '@/services/ApiService';
import Papa from 'papaparse';
import AppTable from '@/components/App/AppTable';

export default {
    name: 'EditHeadingsTables',

    components: { AppTable },

    props: {
        table: {
            type: Object,
            required: true,
        },

        headingsType: {
            type: String,
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

        additionalColumns() {
            return this.additionalInfo.available_data?.columns?.additional || [];
        },
    },

    watch: {
        table: {
            handler(v) {
                window.scroll(0, 0);
                this.getTablePreview(v.id);
            },
            immediate: true,
        },

        headingsType() {
            this.getTablePreview(this.table.id);
        },
    },

    methods: {
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
                    const parsed = await Papa.parse(data[0].preview, {
                        skipEmptyLines: true,
                    });
                    if (preview.column_headings) {
                        preview.column_headings = preview.column_headings.reduce((acc, item) => {
                            return { ...acc, ...item };
                        }, {});
                    }
                    return {
                        id: preview.id,
                        name: preview.name,
                        heading: preview.heading,
                        headings: preview.column_headings,
                        headers: parsed.data[0],
                        data: parsed.data.slice(1),
                        include: true,
                    };
                })
            );
            this.loading = false;
        },

        /**
         * Update heading of specified table
         * @param { string } name
         * @param { string } tableId
         */
        async updateTableHeading(name, tableId) {
            try {
                const { uploadDetails, selections } = this.$store.state;
                await ApiService.updateTableHeading(
                    uploadDetails.type + 's',
                    uploadDetails.id,
                    selections.id,
                    tableId,
                    name
                );
                const table = this.tables.find((table) => table.id === tableId);
                table.heading = name;
            } catch (e) {
                /* istanbul ignore next */
                console.error(e);
            }
        },
    },
};
</script>

<style scoped lang="scss">
.tables {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}
</style>
