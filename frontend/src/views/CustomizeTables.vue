<template>
    <v-row>
        <v-col class="pt-0" cols="12" v-if="selections">
            <v-tabs centered :value="currentTableIndex">
                <v-tab v-for="table in selections.tables" :key="table.id" @click="goTo(table.id)">
                    {{ table.name }}
                </v-tab>
            </v-tabs>
        </v-col>
        <v-col class="pt-7" cols="12" md="8">
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
import CustomizeTablesTable from '@/components/CustomizeTables/CustomizeTablesTable';
import selectionsMixin from '@/mixins/selectionsMixin';

export default {
    name: 'CustomizeTables',

    components: { CustomizeTablesTable },

    mixins: [selectionsMixin],

    computed: {
        currentTableIndex() {
            return this.selections.tables.findIndex((table) => table.id === this.$route.params.id);
        },
        currentTable() {
            return this.selections?.tables[this.currentTableIndex];
        },
    },

    async created() {
        await this.getSelections();
        if (!this.$route.params.id) {
            await this.$router.push({
                path: '/customize-tables/' + this.$store.state.selections.tables[0].id,
                query: this.$route.query,
            });
        }
    },

    methods: {
        /**
         * Go to specified table
         * @param { string } tableId
         */
        goTo(tableId) {
            if (this.currentTable.id === tableId) return;
            this.$router.push({
                path: '/customize-tables/' + tableId,
                query: this.$route.query,
            });
        },

        /**
         * Go to next table or step
         */
        goToNext() {
            if (this.currentTableIndex === this.selections.tables.length - 1) {
                this.$router.push({ path: '/edit-headings', query: this.$route.query });
            } else {
                this.$router.push({
                    path: '/customize-tables/' + this.selections.tables[this.currentTableIndex + 1].id,
                    query: this.$route.query,
                });
            }
        },

        /**
         * Go to previous table if exists
         */
        onBackClick() {
            if (this.currentTableIndex > 0) {
                this.$router.push({
                    path: '/customize-tables/' + this.selections.tables[this.currentTableIndex - 1].id,
                    query: this.$route.query,
                });
            } else {
                this.$router.push({
                    path: '/select-data',
                    query: this.$route.query,
                });
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
            this.goToNext();
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
                this.goToNext();
            }
        },
    },
};
</script>

<style scoped lang="scss">
::v-deep .v-tabs {
    border-radius: 2px;
    border-bottom: 1px solid map-get($colors, 'gray-dark');
    .v-tabs-slider-wrapper {
        display: none !important;
    }
    .v-tab {
        min-width: 114px;
        text-transform: capitalize;
        font-size: 16px;
        letter-spacing: normal;
        font-weight: 300;
        &:hover {
            background-color: map-get($colors, 'gray-light') !important;
        }
        &::before {
            background-color: map-get($colors, 'gray-light') !important;
        }
        &--active {
            color: map-get($colors, 'moody-blue');
            font-weight: 700;
            font-size: 20px;
        }
    }
}
</style>
