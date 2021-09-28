<template>
    <div class="app-table">
        <div class="d-flex align-center" :class="allowActions ? 'mb-1' : 'mb-3 mt-1'">
            <p class="mr-3 fw-300 mb-0">
                <translate>Table</translate>:
                <span :class="{ 'app-table__name--highlighted': highlightName }">
                    {{ name }}
                </span>
            </p>
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
                <v-btn text v-else @click="$emit('restore')" key="restore" :disabled="!canRestore">
                    <v-img height="16" contain src="@/assets/icons/restore.svg" />
                    <translate class="text-link">Restore table</translate>
                </v-btn>
            </div>
        </div>
        <v-simple-table ref="table" v-if="include">
            <template v-slot:default>
                <thead>
                    <tr v-if="headings">
                        <th v-for="(header, i) of headers" :key="`${header} + ${i}`">{{ headings[header] || header }}</th>
                    </tr>
                    <tr>
                        <th v-for="(header, i) of headers" :key="i">{{ header }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, rowIndex) in formattedData" :key="rowIndex">
                        <td
                            v-for="(col, colIndex) in row"
                            :class="{ highlighted: highlightedCols.includes(colIndex) }"
                            :key="colIndex"
                        >
                            <div class="cell">
                                {{ col }}
                            </div>
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
        rowLimit: {
            type: Number,
            default: 3,
        },
        highlightName: {
            type: Boolean,
            default: false,
        },
        parentTable: {
            type: Object,
            default: null,
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
        formattedData() {
            if (this.$route && this.$route.name === 'customize tables') {
                return this.data.slice(0, 5);
            } else {
                return this.data;
            }
        },
        canRestore() {
            if (!this.parentTable) {
                return true;
            } else {
                return this.parentTable.include;
            }
        },
    },

    mounted() {
        this.calculateTableHeight();
    },

    methods: {
        calculateTableHeight() {
            if (this.$refs?.table?.$el && this.rowLimit < this.data.length) {
                const table = this.$refs.table.$el.querySelector('.v-data-table__wrapper');
                const theadHeight = table.querySelector('thead').getBoundingClientRect().height;
                const rows = Array.from(table.querySelectorAll('tbody tr')).slice(0, this.rowLimit);
                const tbodyFirstRowHeight = rows.reduce((acc, row) => acc + row.getBoundingClientRect().height, 0);
                table.style.maxHeight = theadHeight + tbodyFirstRowHeight + 18 + 'px';
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
    .app-table__name--highlighted {
        color: map-get($colors, 'moody-blue');
        font-weight: 700;
    }

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
                word-break: break-all;
                .cell {
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: -webkit-box;
                    -webkit-line-clamp: 5;
                    -webkit-box-orient: vertical;
                }
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
