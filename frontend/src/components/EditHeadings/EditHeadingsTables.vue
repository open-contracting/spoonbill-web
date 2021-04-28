<template>
    <div>
        <v-skeleton-loader class="mt-8" v-if="loading" type="table-tbody"></v-skeleton-loader>

        <div class="mt-8 tables container--full-width" v-else>
            <app-table
                v-for="table in tables"
                :key="table.id"
                :headers="table.headers"
                :name="table.heading || table.name"
                :data="table.data"
                :include="table.include"
                editable-name
                @change-name="updateTableHeading($event, table.id)"
                :headings="table.headings"
                show-first-row
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

    watch: {
        headingsType: {
            handler() {
                this.getAllPreviews();
            },
            immediate: true,
        },
    },

    methods: {
        async getAllPreviews() {
            this.loading = true;
            const previews = await Promise.all(
                this.$store.state.selections.tables.map(async (table) => {
                    return await this.getTablePreview(table.id);
                })
            );
            this.tables = previews.reduce((acc, preview) => {
                return acc.concat(preview);
            }, []);
            this.loading = false;
        },

        /**
         * Fetch and parse preview of table
         * @param { string } tableId
         */
        async getTablePreview(tableId) {
            const { uploadDetails, selections } = this.$store.state;
            const { data } = await ApiService.getTablePreview(
                uploadDetails.type + 's',
                uploadDetails.id,
                selections.id,
                tableId
            );
            return await Promise.all(
                data.map(async (preview) => {
                    const parsed = await Papa.parse(data[0].preview, {
                        skipEmptyLines: true,
                    });
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
