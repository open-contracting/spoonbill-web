<template>
    <div
        class="px-1 table-info"
        :class="{ 'table-info--selected': selected, 'table-info--unavailable': unavailable }"
        v-on="$listeners"
    >
        <v-icon class="pb-1" color="error" v-if="unavailable">mdi-close</v-icon>
        <span class="table-info__name">
            {{ table.name }}
        </span>
        -
        <span class="table-info__details">{{ details }}</span>
    </div>
</template>

<script>
export default {
    name: 'SelectDataTableInfo',

    props: {
        table: {
            type: Object,
            required: true,
        },
        unavailable: {
            type: Boolean,
            default: false,
        },
        selected: {
            type: Boolean,
            default: false,
        },
    },

    computed: {
        details() {
            if (this.unavailable) {
                return this.$gettext('no data');
            } else {
                const { rows, arrays } = this.table;
                const arraysLength = Object.keys(arrays).length;
                let result = this.$gettext('total row count') + ' :' + rows;
                if (arrays) {
                    result += `, ${arraysLength} ${arraysLength > 1 ? this.$gettext('arrays') : this.$gettext('array')}`;
                }
                return result;
            }
        },
    },
};
</script>

<style scoped lang="scss">
.table-info {
    padding: 2px;
    cursor: pointer;
    font-size: 14px;
    &__name {
        text-transform: capitalize;
    }
    &__details {
        font-weight: 300;
    }
    &--selected {
        background-color: map-get($colors, 'accent');
    }
    &--unavailable {
        cursor: default;
    }
}
</style>
