<template>
    <v-card v-if="accent" class="faq-block faq-block--accent">
        <v-card-title>
            <v-icon color="primary">mdi-alert</v-icon>
        </v-card-title>
        <v-card-text>
            <p>
                If you would like to convert CSV data to JSON, please use the older
                <a class="text-link" target="_blank" href="#">Command-Line tool</a>.
            </p>
            <p class="mb-0">
                The JSON data should be in OCDS 1.1 or 1.0, otherwise it may not be possible to flatten. If you. Are
                uncertain whether your data complies with OCDS, use the
                <a class="text-link" target="_blank" href="#">Data Review Tool</a>
                to check first.
            </p>
        </v-card-text>
    </v-card>

    <v-card v-else class="faq-block">
        <v-card-title>FAQ</v-card-title>
        <v-card-text>
            <v-expansion-panels accordion>
                <v-expansion-panel v-for="item in items" :key="item.title">
                    <v-expansion-panel-header hide-actions class="d-flex" v-slot="{ open }">
                        <v-icon v-show="open" color="accent">mdi-minus-circle</v-icon>
                        <v-icon v-show="!open">mdi-plus-circle</v-icon>
                        {{ item.title }}
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                        {{ item.content }}
                    </v-expansion-panel-content>
                </v-expansion-panel>
            </v-expansion-panels>
        </v-card-text>
    </v-card>
</template>

<script>
export default {
    name: 'SelectDataFAQ',

    props: {
        accent: {
            type: Boolean,
            default: false,
        },
    },

    data() {
        return {
            items: [
                {
                    title: 'What is OCDS Lite?',
                    content:
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
                {
                    title: 'What is OCDS schema version 1.1?',
                    content:
                        'Lorem ipsum dolor sit amet, adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
                {
                    title: 'What is the data review tool?',
                    content:
                        'Lorem ipsum dolor sit amet, adipiscing elit, sed ' +
                        'do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, ' +
                        'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
                },
            ],
        };
    },
};
</script>

<style scoped lang="scss">
.faq-block {
    position: sticky;
    top: 130px;
    width: 100%;
    border: 4px solid map-get($colors, 'primary');
    border-radius: 32px 4px 4px 4px !important;
    min-height: 580px;
    box-shadow: none !important;
    .v-card__title {
        font-size: 24px;
        border-bottom: 1px solid map-get($colors, 'gray-light');
    }
    .v-card__text {
        padding-left: 0;
        padding-right: 0;
    }
    &.faq-block--accent {
        border-color: map-get($colors, 'accent');
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
    &-header,
    &-content__wrap {
        padding-left: 16px;
        padding-right: 16px;
    }
    &::before {
        box-shadow: none;
    }
    &-header > *:not(.v-expansion-panel-header__icon) {
        flex: 0 0 auto;
        margin-left: -3px;
        margin-right: 8px;
    }
}
</style>
