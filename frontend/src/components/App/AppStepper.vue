<template>
    <v-stepper alt-labels class="app-stepper" :value="value">
        <v-stepper-header>
            <v-stepper-step :complete="value > 1" complete-icon="mdi-check" step="1">
                <span class="text-link" @click="onUploadFileStepClick" v-if="value > 1 || $store.state.numberOfUploads">
                    Re-upload file
                </span>
                <template v-else>Upload file</template>
            </v-stepper-step>

            <v-divider :class="{ active: value > 1, complete: value > 2 }"></v-divider>

            <v-stepper-step :complete="value > 2" complete-icon="mdi-check" step="2">
                <span :class="{ 'text-link': value > 2 }" @click="navigateTo('/select-data')">Select data</span>
            </v-stepper-step>

            <v-divider :class="{ active: value > 2, complete: value > 3 }"></v-divider>

            <v-stepper-step :complete="value > 3" complete-icon="mdi-check" step="3">Customize tables</v-stepper-step>

            <v-divider :class="{ active: value > 3, complete: value > 4 }"></v-divider>

            <v-stepper-step :complete="value > 4" complete-icon="mdi-check" step="4">Edit headings</v-stepper-step>

            <v-divider :class="{ active: value > 4, complete: value > 5 }"></v-divider>

            <v-stepper-step step="5">Download</v-stepper-step>
        </v-stepper-header>
    </v-stepper>
</template>

<script>
export default {
    name: 'AppStepper',

    computed: {
        value() {
            const route = this.$route.name;
            switch (route) {
                case 'select data':
                    return 2;
                case 'customize tables':
                    return 3;
                default:
                    return 1;
            }
        },
    },

    methods: {
        /**
         * Goes to the first step and clears upload details after confirmation
         */
        async onUploadFileStepClick() {
            const confirmed = await this.openConfirmDialog();
            if (confirmed) {
                this.$store.commit('setUploadDetails', null);
                this.$store.commit('setSelections', null);
                this.$router.push('/upload-file').catch(() => {});
            }
        },

        /**
         * Goes to specified path saving current route query after confirmation
         * @param { string } path
         */
        async navigateTo(path) {
            const confirmed = await this.openConfirmDialog();
            if (confirmed) {
                this.$router.push({ path, query: this.$route.query });
            }
        },

        async openConfirmDialog() {
            return await this.$root.openConfirmDialog({
                title: 'Are you sure to go back?',
                content: 'When going to the previous step, all current changes will be reversed',
                submitBtnText: 'Yes, go back',
                icon: require('@/assets/icons/back.svg'),
            });
        },
    },
};
</script>

<style scoped lang="scss">
.app-stepper.v-stepper {
    box-shadow: none;
    background-color: map-get($colors, 'super-light');
    ::v-deep .v-stepper__header {
        .v-divider {
            margin: 49px -80px 0;
            border: 1px solid map-get($colors, 'gray-light');
            &.active {
                border-color: map-get($colors, 'accent');
            }
            &.complete {
                border-color: map-get($colors, 'primary');
            }
        }
        .v-stepper__step {
            &--inactive .v-stepper__step__step {
                background-color: map-get($colors, 'gray-light') !important;
            }
            &--active {
                .v-stepper__step__step {
                    background-color: map-get($colors, 'accent') !important;
                    position: relative;
                    &::after {
                        content: '';
                        position: absolute;
                        left: 3px;
                        top: 3px;
                        width: 38px;
                        height: 38px;
                        border: 2px solid white;
                        border-radius: 50%;
                    }
                }
                & + .v-divider {
                    position: relative;
                    &::before {
                        content: '';
                        position: absolute;
                        border: 1px solid map-get($colors, 'accent');
                        left: 0;
                        top: -1px;
                        width: 50%;
                        z-index: 2;
                    }
                }
            }
            &:not(.v-stepper__step--active):not(.v-stepper__step--inactive) {
                .v-stepper__step__step {
                    background-color: map-get($colors, 'primary');
                }
                & + .v-divider {
                    position: relative;
                    &::before {
                        content: '';
                        position: absolute;
                        border: 1px solid map-get($colors, 'primary');
                        left: 0;
                        top: -1px;
                        width: 50%;
                        z-index: 2;
                    }
                }
            }
            .v-stepper__step__step {
                margin: 4px 4px 13px;
                width: 44px !important;
                height: 44px;
                color: map-get($colors, 'primary');
                position: relative;
                z-index: 3;
            }
            .v-stepper__label {
                margin-top: 8px;
                font-weight: 400;
                color: map-get($colors, 'primary');
                text-shadow: none;
            }
        }
    }
}
</style>
