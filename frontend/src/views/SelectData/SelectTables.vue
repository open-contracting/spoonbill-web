<template>
    <v-container>
        <v-row class="pt-6 pb-8">
            <v-col cols="12" md="8" xl="8">
                <layout-info />
                <h2 class="page-title">Select a JSON file to flatten</h2>

                <p class="page-description">
                    Choose the available tables that you want to flatten and add them to selected tables to continue. Tables
                    that are unavailable were not found in the data.
                </p>

                <v-container>
                    <v-row>
                        <v-col class="pa-0" cols="5">
                            <p class="column-name">Available tables</p>
                            <draggable class="tables-list" v-model="availableTables" group="tables">
                                <div class="list-item" v-for="table in availableTables" :key="table.id">
                                    <span class="table-name">
                                        {{ table.name }}
                                    </span>
                                    -
                                    {{ table.details }}
                                </div>
                            </draggable>
                        </v-col>
                        <v-col class="pa-0" cols="5" offset="2">
                            <p class="column-name">Selected tables</p>
                            <draggable class="tables-list" v-model="selectedTables" group="tables">
                                <div class="list-item" v-for="table in selectedTables" :key="table.id">
                                    <span class="table-name">
                                        {{ table.name }}
                                    </span>
                                    -
                                    {{ table.details }}
                                </div>
                            </draggable>
                        </v-col>
                    </v-row>
                </v-container>
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
            availableTables: [
                {
                    id: '1',
                    name: 'Parties',
                    details: 'total row count: 14, 1 array',
                },
                {
                    id: '2',
                    name: 'Tenders',
                    details: 'total row count: 8, 2 array',
                },
                {
                    id: '3',
                    name: 'Awards',
                    details: 'total row count: 4, 0 array',
                },
                {
                    id: '4',
                    name: 'Contracts',
                    details: 'total row count: 2, 1 array',
                },
                {
                    id: '5',
                    name: 'Documents',
                    details: 'total row count: 3, 1 array',
                },
            ],
            selectedTables: [],
        };
    },
};
</script>

<style scoped lang="scss">
.column-name {
    font-weight: 300;
    margin-bottom: 8px;
}
.tables-list {
    padding: 24px;
    border: 1px solid map-get($colors, 'gray-dark');
    background-color: #ffffff;
    min-height: 230px;
    width: 100%;
    height: 100%;
}
.list-item {
    cursor: pointer;
    &:not(:last-child) {
        margin-bottom: 5px;
    }
}
</style>
