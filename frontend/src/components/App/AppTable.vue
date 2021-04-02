<template>
    <div class="app-table">
        <div class="mb-4 d-flex justify-space-between align-center">
            <p class="fw-300 mb-0 app-table__name">{{ name }}</p>
            <slot name="actions" />
        </div>
        <v-simple-table :style="{ width: headers.length * 100 + 'px' }">
            <template v-slot:default>
                <thead>
                    <tr>
                        <th v-for="header of headers" :key="header">{{ header }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, rowIndex) in data" :key="rowIndex">
                        <td v-for="(col, colIndex) in row" :key="colIndex">{{ col }}</td>
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
    },
};
</script>

<style scoped lang="scss">
.app-table {
    &__name {
    }

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
            max-width: 100px;
            background-color: #facd91;
        }
    }
}
</style>
