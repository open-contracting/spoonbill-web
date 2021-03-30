<template>
    <v-row>
        <v-col cols="12" md="8" xl="8">
            <layout-info />
            <h2 class="page-title">Select data to flatten to Excel/CSV</h2>

            <p class="page-description">
                Choose the available tables that you want to flatten and add them to selected tables to continue. Tables that
                are unavailable were not found in the data.
            </p>

            <v-container class="mt-9">
                <v-row v-click-outside="clearSelection" class="tables-wrapper">
                    <v-col class="pa-0 pr-2" cols="12" lg="5">
                        <div>
                            <p class="column-name">Available tables</p>
                            <draggable @start="clearSelection" class="tables-list" v-model="availableTables" group="tables">
                                <select-data-table-info
                                    v-for="table in availableTables"
                                    :table="table"
                                    :key="table.name"
                                    :selected="checkedTables.includes(table.name)"
                                    @click="onTableClick($event, table.name)"
                                />
                            </draggable>
                        </div>
                    </v-col>
                    <v-col
                        class="my-5 my-lg-0 py-0 px-2 d-flex flex-lg-column align-center justify-end justify-lg-center"
                        cols="12"
                        lg="2"
                    >
                        <v-btn
                            :disabled="!isAddAllowed"
                            @click="addTables"
                            class="app-btn add-btn mr-4 mr-lg-0"
                            color="gray-light"
                            width="120"
                            height="44"
                        >
                            <v-img class="mr-2" max-width="24" src="@/assets/icons/arrow-in-circle.svg" />
                            Add
                        </v-btn>

                        <v-btn
                            :disabled="!isRemoveAllowed"
                            @click="removeTables"
                            class="mt-lg-5 app-btn remove-btn"
                            color="gray-light"
                            width="120"
                            height="44"
                        >
                            <v-img class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                            Remove
                        </v-btn>
                    </v-col>
                    <v-col class="pa-0 pl-2" cols="12" lg="5">
                        <div>
                            <p class="column-name">Selected tables</p>
                            <draggable @start="clearSelection" class="tables-list" v-model="selectedTables" group="tables">
                                <select-data-table-info
                                    v-for="table in selectedTables"
                                    :table="table"
                                    :key="table.name"
                                    :selected="checkedTables.includes(table.name)"
                                    @click="onTableClick($event, table.name)"
                                />
                            </draggable>
                        </div>
                    </v-col>
                </v-row>
            </v-container>
            <div class="mt-6" v-if="unavailableTables.length">
                <p class="mb-4 column-name">Unavailable tables</p>
                <select-data-table-info v-for="table in unavailableTables" :key="table.name" :table="table" unavailable />
            </div>
            <div class="mt-15 d-flex justify-end">
                <v-btn @click="onContinueClick" :disabled="!selectedTables.length" color="accent" height="56" width="152">
                    <v-img max-width="24" class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                    Continue
                </v-btn>
            </div>
        </v-col>
    </v-row>
</template>

<script>
import LayoutInfo from '@/components/Layout/LayoutInfo';
import draggable from 'vuedraggable';
import SelectDataTableInfo from '@/components/SelectData/SelectDataTableInfo';

export default {
    name: 'SelectData',

    components: { SelectDataTableInfo, LayoutInfo, draggable },

    data() {
        return {
            /** @type { ?string } */
            selectedTableName: null,
            checkedTables: [],
            availableTables: [],
            selectedTables: [],
            unavailableTables: [],
        };
    },

    computed: {
        isAddAllowed() {
            return this.checkedTables.length && this.availableTables.some((table) => table.name === this.checkedTables[0]);
        },

        isRemoveAllowed() {
            return this.checkedTables.length && this.selectedTables.some((table) => table.name === this.checkedTables[0]);
        },
    },

    created() {
        const allTables = this.$store.state.uploadDetails.available_tables || [];
        this.availableTables = allTables.filter((table) => table.available_data);
        this.unavailableTables = allTables.filter((table) => !table.available_data);
    },

    methods: {
        /**
         * Handle click on table
         * @param { MouseEvent } ev
         * @param { string } tableName
         */
        onTableClick(ev, tableName) {
            if (!this.checkedTables.length || (!ev.ctrlKey && !ev.shiftKey)) {
                this.checkedTables = [tableName];
                return;
            }
            if ((ev.ctrlKey || ev.shiftKey) && this.checkedTables.includes(tableName)) {
                this.checkedTables.splice(
                    this.checkedTables.findIndex((table) => table === tableName),
                    1,
                );
                return;
            }
            if (ev.ctrlKey && this.isInTheSameSection(this.checkedTables[0], tableName)) {
                this.checkedTables.push(tableName);
            }
        },

        /**
         * Check if tables are in the same section
         * @param { string } firstTName
         * @param { string } secondTName
         * @return { boolean }
         */
        isInTheSameSection(firstTName, secondTName) {
            return (
                this.availableTables.findIndex((table) => table.name === firstTName) > -1 ===
                this.availableTables.findIndex((table) => table.name === secondTName) > -1
            );
        },

        /**
         * Add selected tables to 'Selected tables'
         */
        addTables() {
            this.checkedTables.forEach((tableName) => {
                const index = this.availableTables.findIndex((table) => table.name === tableName);
                if (index > -1) {
                    this.selectedTables.push(...this.availableTables.splice(index, 1));
                }
            });
            this.clearSelection();
        },

        /**
         * Remove selected tables from 'Selected tables'
         */
        removeTables() {
            this.checkedTables.forEach((tableName) => {
                const index = this.selectedTables.findIndex((table) => table.name === tableName);
                if (index > -1) {
                    this.availableTables.push(...this.selectedTables.splice(index, 1));
                }
            });
            this.clearSelection();
        },

        /**
         * Clear selected table
         */
        clearSelection() {
            this.checkedTables = [];
        },

        /**
         * Go to the 'customize tables' step
         */
        onContinueClick() {
            this.$router.push({ path: '/customize-tables', query: this.$route.query });
        },
    },
};
</script>

<style scoped lang="scss">
.tables-wrapper {
    ::v-deep {
        .v-btn .v-btn__content {
            justify-content: flex-start;
        }
        .remove-btn .v-image {
            transform: rotateZ(180deg);
        }
        @media #{map-get($display-breakpoints, 'md-and-down')} {
            .add-btn .v-image {
                transform: rotateZ(90deg);
            }
            .remove-btn .v-image {
                transform: rotateZ(270deg);
            }
        }
    }
}
.column-name {
    font-weight: 300;
    margin-bottom: 8px;
}
.tables-list {
    padding: 24px 20px;
    border: 1px solid map-get($colors, 'gray-dark');
    background-color: #ffffff;
    min-height: 230px;
    width: 100%;
    height: 100%;
    .table-info:not(:last-child) {
        margin-bottom: 5px;
    }
}
</style>
