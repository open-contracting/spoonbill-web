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
import getSelectionsMixin from '@/mixins/getSelectionsMixin';

export default {
    name: 'CustomizeTables',

    components: { CustomizeTablesTable, LayoutInfo },

    mixins: [getSelectionsMixin],

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
            if (this.currentTableIndex === this.selections.tables.length - 1) {
                this.$router.push({ path: '/edit-headings', query: this.$route.query });
            } else {
                this.currentTableIndex++;
                this.currentTable = this.selections.tables[this.currentTableIndex];
            }
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
