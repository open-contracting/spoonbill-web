<template>
    <v-card class="faq-block">
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
    name: 'FAQ',

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
    max-width: 377px;
    width: 100%;
    border: 4px solid map-get($colors, 'gray-dark');
    border-radius: 0 !important;
    border-top-left-radius: 20px !important;
    .v-card__title {
        font-size: 24px;
        border-bottom: 1px solid map-get($colors, 'gray-light');
    }
    .v-card__text {
        padding-left: 0;
        padding-right: 0;
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
