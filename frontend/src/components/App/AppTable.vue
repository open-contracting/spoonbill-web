<template>
    <div class="app-table">
        <div class="d-flex align-center" :class="allowActions ? 'mb-1' : 'mb-3 mt-1'">
            <p class="mr-3 fw-300 mb-0 app-table__name">{{ name }}</p>
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
        <v-simple-table v-if="include" :style="{ width: headers.length * 100 + 'px' }">
            <template v-slot:default>
                <thead>
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
            required: true,
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
};
</script>

<style scoped lang="scss">
.app-table {
    max-width: 100%;

    ::v-deep table {
        border-collapse: collapse !important;
        th,
        td {
            border: 1px solid map-get($colors, 'darkest');
            text-align: center !important;
            font-size: 14px !important;
            font-weight: 300;
            color: map-get($colors, 'darkest') !important;
        }
        th {
            min-width: 100px;
            background-color: #facd91;
        }
        td.highlighted {
            background-color: #b6bafd;
        }
    }
}
</style>
