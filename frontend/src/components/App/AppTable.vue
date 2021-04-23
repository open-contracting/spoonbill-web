<template>
    <div class="app-table">
        <div class="d-flex align-center" :class="allowActions ? 'mb-1' : 'mb-3 mt-1'">
            <p class="mr-3 fw-300 mb-0 app-table__name">Table: {{ name }}</p>
            <div v-if="editableName">
                <v-menu :close-on-content-click="false" v-model="nameMenu">
                    <template v-slot:activator="{ on, attrs }">
                        <v-btn text v-bind="attrs" v-on="on">
                            <v-img height="16" contain src="@/assets/icons/pencil.svg" />
                            <translate class="text-link">Edit</translate>
                        </v-btn>
                    </template>

                    <v-text-field autofocus solo hide-details v-model="newName">
                        <div slot="append">
                            <v-btn class="mr-2" width="24" height="24" icon :disabled="!newName" @click="changeName">
                                <v-icon class="pb-1" size="18" color="success">mdi-check</v-icon>
                            </v-btn>

                            <v-btn width="24" height="24" icon @click="nameMenu = false">
                                <v-icon class="pb-1" size="18" color="error">mdi-close</v-icon>
                            </v-btn>
                        </div>
                    </v-text-field>
                </v-menu>
            </div>

            <div v-if="allowActions">
                <v-btn text v-if="include" @click="$emit('remove')" key="remove">
                    <v-img height="16" contain src="@/assets/icons/remove.svg" />
                    <translate class="text-link">Remove</translate>
                </v-btn>
                <v-btn text v-else @click="$emit('restore')" key="restore">
                    <v-img height="16" contain src="@/assets/icons/restore.svg" />
                    <translate class="text-link">Restore table</translate>
                </v-btn>
            </div>
        </div>
        <v-simple-table ref="table" v-if="include" :style="{ width: headers.length * 100 + 'px' }">
            <template v-slot:default>
                <thead>
                    <tr v-if="headings">
                        <th v-for="header of headers" :key="header">{{ headings[header] || header }}</th>
                    </tr>
                    <tr>
                        <th v-for="header of headers" :key="header">{{ header }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, rowIndex) in data" :key="rowIndex">
                        <td
                            v-for="(col, colIndex) in row"
                            :class="{ highlighted: highlightedCols.includes(colIndex) }"
                            :key="colIndex"
                        >
                            {{ col }}
                        </td>
                    </tr>
                </tbody>
            </template>
        </v-simple-table>
    </div>
</template>

<script>
export default {
    name: 'AppTable',

    props: {
        name: {
            type: String,
            required: true,
        },
        headers: {
            type: Array,
            required: true,
        },
        data: {
            type: Array,
            required: true,
        },
        include: {
            type: Boolean,
            default: true,
        },
        allowActions: {
            type: Boolean,
            default: false,
        },
        additionalColumns: {
            type: Array,
            default: () => [],
        },
        editableName: {
            type: Boolean,
            default: false,
        },
        headings: {
            type: Object,
            default: null,
        },
        showFirstRow: {
            type: Boolean,
            default: false,
        },
    },

    data() {
        return {
            nameMenu: false,
            newName: null,
        };
    },

    watch: {
        nameMenu() {
            this.newName = this.name;
        },

        async headings() {
            await this.$nextTick();
            this.calculateTableHeight();
        },
    },

    computed: {
        highlightedCols() {
            return this.headers.reduce((acc, header, idx) => {
                if (this.additionalColumns.includes(header)) {
                    acc.push(idx);
                }
                return acc;
            }, []);
        },
    },

    mounted() {
        this.calculateTableHeight();
    },

    methods: {
        calculateTableHeight() {
            /* istanbul ignore next */
            if (this.showFirstRow) {
                const table = this.$refs.table.$el.querySelector('.v-data-table__wrapper');
                const theadHeight = table.querySelector('thead').getBoundingClientRect().height;
                const tbodyFirstRowHeight = table.querySelector('tbody tr').getBoundingClientRect().height;
                table.style.maxHeight = theadHeight + tbodyFirstRowHeight + 15 + 'px';
                table.style.overflowY = 'auto';
            }
        },

        changeName() {
            this.$emit('change-name', this.newName);
            this.nameMenu = false;
        },
    },
};
</script>

<style scoped lang="scss">
.app-table {
    max-width: 100%;

    ::v-deep .v-data-table__wrapper {
        overflow: auto;
        table {
            border-collapse: collapse !important;
            th,
            td {
                padding: 4px !important;
                border: 1px solid map-get($colors, 'darkest');
                text-align: center !important;
                font-size: 14px !important;
                font-weight: 300;
                color: map-get($colors, 'darkest') !important;
                max-width: 100px;
                word-break: break-all;
            }
            th {
                min-width: 100px;
                background-color: map-get($colors, 'gray-light');
            }
            td.highlighted {
                background-color: #b6bafd;
            }
        }
    }
}
</style>
