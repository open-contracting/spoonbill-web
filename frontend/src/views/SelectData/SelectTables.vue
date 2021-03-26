<template>
    <v-container>
        <v-row class="pt-6 pb-8">
            <v-col cols="12" md="8" xl="8">
                <layout-info />
                <h2 class="page-title">Select data to flatten to Excel/CSV</h2>

                <p class="page-description">
                    Choose the available tables that you want to flatten and add them to selected tables to continue. Tables
                    that are unavailable were not found in the data.
                </p>

                <v-container class="mt-9">
                    <v-row v-click-outside="clearSelection">
                        <v-col class="pa-0 pr-2" cols="5">
                            <div>
                                <p class="column-name">Available tables</p>
                                <draggable class="tables-list" v-model="availableTables" group="tables">
                                    <div
                                        class="px-1 table-info"
                                        v-for="table in availableTables"
                                        :key="table.id"
                                        :class="{ selected: selectedTableId === table.id }"
                                        @click="selectedTableId = table.id"
                                    >
                                        <span class="table-info__name">
                                            {{ table.name }}
                                        </span>
                                        -
                                        <span class="table-info__details">
                                            {{ table.details }}
                                        </span>
                                    </div>
                                </draggable>
                            </div>
                        </v-col>
                        <v-col class="py-0 px-2 d-flex flex-column align-center justify-center" cols="2">
                            <v-btn
                                :disabled="!isAddAllowed"
                                @click="addTable()"
                                class="app-btn"
                                color="gray-light"
                                width="120"
                                height="44"
                            >
                                <v-img class="mr-2" max-width="24" src="@/assets/icons/arrow-in-circle.svg" />
                                Add
                            </v-btn>

                            <v-btn
                                :disabled="!isRemoveAllowed"
                                @click="removeTable"
                                class="mt-5 app-btn"
                                color="gray-light"
                                width="120"
                                height="44"
                            >
                                <v-img class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                                Remove
                            </v-btn>
                        </v-col>
                        <v-col class="pa-0 pl-2" cols="5">
                            <div>
                                <p class="column-name">Selected tables</p>
                                <draggable class="tables-list" v-model="selectedTables" group="tables">
                                    <div
                                        class="px-1 table-info"
                                        v-for="table in selectedTables"
                                        :key="table.id"
                                        :class="{ selected: selectedTableId === table.id }"
                                        @click="selectedTableId = table.id"
                                    >
                                        <span class="table-info__name">
                                            {{ table.name }}
                                        </span>
                                        -
                                        <span class="table-info__details">
                                            {{ table.details }}
                                        </span>
                                    </div>
                                </draggable>
                            </div>
                        </v-col>
                    </v-row>
                </v-container>
                <div class="mt-6">
                    <p class="mb-4 column-name">Unavailable tables</p>
                    <div class="table-info" v-for="table in unavailableTables" :key="table.id">
                        <v-icon color="#FF9393">mdi-close</v-icon>
                        <span class="table-info__name">
                            {{ table.name }}
                        </span>
                        -
                        <span class="table-info__details">
                            {{ table.details }}
                        </span>
                    </div>
                </div>
                <div class="mt-15 d-flex justify-end">
                    <v-btn class="mr-6" color="gray-light" height="56" width="122"> Start over </v-btn>

                    <v-btn color="accent" height="56" width="152">
                        <v-img max-width="24" class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                        Continue
                    </v-btn>
                </div>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import LayoutInfo from '@/components/Layout/LayoutInfo';
import draggable from 'vuedraggable';

export default {
    name: 'SelectFile',

    components: { LayoutInfo, draggable },

    data() {
        return {
            selectedTableId: null,
            availableTables: [
                {
                    id: '1',
                    name: 'MOCKED',
                    details: 'total row count: 14, 1 array',
                },
                {
                    id: '2',
                    name: 'MOCKED',
                    details: 'total row count: 8, 2 array',
                },
                {
                    id: '3',
                    name: 'MOCKED',
                    details: 'total row count: 4, 0 array',
                },
            ],
            selectedTables: [],
            unavailableTables: [
                {
                    id: '4',
                    name: 'MOCKED',
                    details: 'no data',
                },
                {
                    id: '5',
                    name: 'MOCKED',
                    details: 'no data',
                },
                {
                    id: '6',
                    name: 'MOCKED',
                    details: 'no data',
                },
            ],
        };
    },

    computed: {
        isAddAllowed() {
            return this.selectedTableId && this.availableTables.some((table) => table.id === this.selectedTableId);
        },

        isRemoveAllowed() {
            return this.selectedTableId && this.selectedTables.some((table) => table.id === this.selectedTableId);
        },
    },

    methods: {
        /**
         * Add selected table to 'Selected tables'
         */
        addTable() {
            const index = this.availableTables.findIndex((table) => table.id === this.selectedTableId);
            if (index > -1) {
                this.selectedTables.push(...this.availableTables.splice(index, 1));
                this.clearSelection();
            }
        },

        /**
         * Remove selected table from 'Selected tables'
         */
        removeTable() {
            const index = this.selectedTables.findIndex((table) => table.id === this.selectedTableId);
            if (index > -1) {
                this.availableTables.push(...this.selectedTables.splice(index, 1));
                this.clearSelection();
            }
        },

        /**
         * Clear selected table
         */
        clearSelection() {
            this.selectedTableId = null;
        },
    },
};
</script>

<style scoped lang="scss">
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
.table-info {
    padding: 1px 0;
    cursor: pointer;
    font-size: 14px;
    border: 1px dashed transparent;
    &__details {
        font-weight: 300;
    }
    &.selected {
        border-color: map-get($colors, 'primary');
    }
}
</style>
