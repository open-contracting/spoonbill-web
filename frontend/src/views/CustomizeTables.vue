<template>
    <v-row>
        <v-col cols="12" md="8" xl="8">
            <layout-info />
            <translate tag="h2" class="page-title">Customize Tables</translate>
        </v-col>
        <v-col cols="12">
            <customize-tables-table
                v-if="currentTable"
                :table="currentTable"
                @remove="onRemoveClick"
                @save="onContinueClick"
                @back="onBackClick"
            />
        </v-col>
    </v-row>
</template>

<script>
import LayoutInfo from '@/components/Layout/LayoutInfo';
import CustomizeTablesTable from '@/components/CustomizeTables/CustomizeTablesTable';
import getQueryParam from '@/utils/getQueryParam';

export default {
    name: 'CustomizeTables',

    components: { CustomizeTablesTable, LayoutInfo },

    computed: {
        selections() {
            return this.$store.state.selections;
        },
    },

    data() {
        return {
            currentTable: null,
            currentTableIndex: 0,
        };
    },

    async created() {
        const selectionsId = getQueryParam('selections');
        if (selectionsId && !this.selections) {
            await this.$store.dispatch('fetchSelections', selectionsId);
            if (!this.selections) {
                this.$router.push({
                    path: '/upload-file',
                    query: this.$route.query,
                });
                return;
            }
        }
        this.currentTable = this.selections.tables[0];
    },

    methods: {
        /**
         * Go to previous table if exists
         */
        onBackClick() {
            if (this.currentTableIndex > 0) {
                this.currentTableIndex--;
                this.currentTable = this.selections.tables[this.currentTableIndex];
            }
        },

        /**
         * Set true value for table's 'include' status and opens next table
         */
        async onContinueClick() {
            await this.$store.dispatch('updateIncludeStatus', {
                tableId: this.currentTable.id,
                value: true,
            });
            this.currentTableIndex++;
            this.currentTable = this.selections.tables[this.currentTableIndex];
        },

        /**
         * Set false value for table's 'include' status and opens next table
         */
        async onRemoveClick() {
            const confirmed = await this.$root.openConfirmDialog({
                title: this.$gettext('Are you sure?'),
                content: this.$gettext('Removing this table will mean it will not be included in flattened Excel file'),
                submitBtnText: this.$gettext('Yes, remove table and continue'),
                icon: require('@/assets/icons/remove.svg'),
            });
            if (confirmed) {
                await this.$store.dispatch('updateIncludeStatus', {
                    tableId: this.currentTable.id,
                    value: false,
                });
                this.currentTableIndex++;
                this.currentTable = this.selections.tables[this.currentTableIndex];
            }
        },
    },
};
</script>

<style scoped lang="scss"></style>
