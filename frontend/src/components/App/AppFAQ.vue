<template>
    <v-card class="mt-2 faq-block">
        <v-card-title>
            <slot name="title" />
        </v-card-title>
        <v-card-text>
            <slot />
        </v-card-text>
    </v-card>
</template>

<script>
export default {
    name: 'AppFAQ',

    props: {
        accent: {
            type: Boolean,
            default: false,
        },
    },
};
</script>

<style scoped lang="scss">
.faq-block {
    position: sticky;
    top: 130px;
    width: 100%;
    border: 4px solid map-get($colors, 'accent');
    border-radius: 32px 4px 4px 4px !important;
    box-shadow: none !important;
    .v-card__title {
        font-size: 24px;
    }
    .v-card__text {
        padding: 0;
        font-weight: 300;
    }
    &.faq-block--accent {
        min-height: auto;
        .v-card__title {
            border: none;
        }
        .v-card__text {
            padding: 20px;
            color: map-get($colors, 'primary');
        }
    }
}
::v-deep .v-expansion-panel {
    border-top: 1px solid map-get($colors, 'gray-light');
    padding: 5px 0;
    &:not(:first-child)::after {
        border-top: none;
    }
    &-header,
    &-content__wrap {
        padding-left: 16px;
        padding-right: 16px;
    }
    &::before {
        box-shadow: none;
    }
    &-header {
        font-weight: 400;
        .v-icon {
            color: map-get($colors, 'darkest') !important;
        }
        &--active .v-icon {
            color: map-get($colors, 'accent') !important;
        }
    }
}
</style>
