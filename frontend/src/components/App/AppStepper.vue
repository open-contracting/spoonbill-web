<template>
    <v-stepper alt-labels class="app-stepper" :value="value" v-if="!isOcdsLite">
        <v-stepper-header v-if="!hideFirstStep">
            <v-stepper-step :complete="value > 1" complete-icon="mdi-pencil" step="1" @click="navigateTo(1, '/upload-file')">
                <translate class="text-link" v-if="$store.state.numberOfUploads > 0 || value > 1" key="re">
                    Re-upload file
                </translate>
                <translate translate-context="Upload file" key="upload" v-else>Upload file</translate>
            </v-stepper-step>

            <v-divider :class="{ active: value > 1, complete: value > 2 }"></v-divider>

            <v-stepper-step
                :complete="value > 2"
                complete-icon="mdi-pencil"
                :step="2"
                @click="navigateTo(2, '/select-data', isOcdsLite)"
            >
                <translate :class="{ 'text-link': value > 2 }">Select data</translate>
            </v-stepper-step>

            <v-divider :class="{ active: value > 2, complete: value > 3 }"></v-divider>

            <v-stepper-step
                :complete="value > 3"
                complete-icon="mdi-pencil"
                step="3"
                @click="navigateTo(3, '/customize-tables', isOcdsLite)"
            >
                <translate :class="{ 'text-link': value > 3 }">Preview tables</translate>
            </v-stepper-step>

            <v-divider :class="{ active: value > 3, complete: value > 4 }"></v-divider>

            <v-stepper-step
                :complete="value > 4"
                complete-icon="mdi-pencil"
                step="4"
                @click="navigateTo(4, '/edit-headings', isOcdsLite)"
            >
                <translate :class="{ 'text-link': value > 4 }">Edit headings</translate>
            </v-stepper-step>

            <v-divider :class="{ active: value > 4, complete: value > 5 }"></v-divider>

            <v-stepper-step step="5">
                <translate>Download</translate>
            </v-stepper-step>
        </v-stepper-header>
        <v-stepper-header v-else>
            <v-stepper-step
                :complete="value > 1"
                complete-icon="mdi-pencil"
                :step="1"
                @click="navigateTo(1, '/select-data', isOcdsLite)"
            >
                <translate :class="{ 'text-link': value > 2 }">Select data</translate>
            </v-stepper-step>

            <v-divider :class="{ active: value > 1, complete: value > 2 }"></v-divider>

            <v-stepper-step
                :complete="value > 2"
                complete-icon="mdi-pencil"
                step="2"
                @click="navigateTo(2, '/customize-tables', isOcdsLite)"
            >
                <translate :class="{ 'text-link': value > 2 }">Preview tables</translate>
            </v-stepper-step>

            <v-divider :class="{ active: value > 2, complete: value > 3 }"></v-divider>

            <v-stepper-step
                :complete="value > 3"
                complete-icon="mdi-pencil"
                step="3"
                @click="navigateTo(3, '/edit-headings', isOcdsLite)"
            >
                <translate :class="{ 'text-link': value > 3 }">Edit headings</translate>
            </v-stepper-step>

            <v-divider :class="{ active: value > 3, complete: value > 4 }"></v-divider>

            <v-stepper-step step="4">
                <translate>Download</translate>
            </v-stepper-step>
        </v-stepper-header>
    </v-stepper>
</template>

<script>
export default {
    name: 'AppStepper',

    computed: {
        value() {
            const route = this.$route.name;
            /* istanbul ignore next */
            if (!this.hideFirstStep) {
                switch (route) {
                    case 'select data':
                        return 2;
                    case 'customize tables':
                        return 3;
                    case 'edit headings':
                        return 4;
                    case 'download':
                        return 5;
                    default:
                        return 1;
                }
            } else {
                switch (route) {
                    case 'select data':
                        return 1;
                    case 'customize tables':
                        return 2;
                    case 'edit headings':
                        return 3;
                    case 'download':
                        return 4;
                    default:
                        return 1;
                }
            }
        },
        isOcdsLite() {
            return this.$store.state.selections && this.$store.state.selections.kind === 'ocds_lite';
        },
        hideFirstStep() {
            // return this.$store.getters.isFileFromDataRegistry;
            return this.$store.getters.isFileFromDataRegistry;
        },
    },

    methods: {
        /**
         * Go to specified path
         * @param { number } step
         * @param { string } path
         * @param { boolean } disable
         */
        async navigateTo(step, path, disable = false) {
            if (disable) return;
            if (this.value === 1 && step === 1 && this.$store.state.numberOfUploads > 0) {
                const confirmed = await this.$root.openConfirmDialog();
                if (confirmed) {
                    this.$store.commit('setUploadDetails', null);
                    this.$store.commit('setSelections', null);
                }
                return;
            }

            if (this.value <= step) return;
            let query = {};
            if (path === '/upload-file') {
                if (this.$route.query.lang) {
                    query.lang = this.$route.query.lang;
                }
            } else {
                query = {
                    ...this.$route.query,
                };
            }
            this.$router.push({ path, query }).catch(() => {});
        },
    },
};
</script>

<style scoped lang="scss">
.app-stepper.v-stepper {
    margin: 0 auto;
    max-width: 815px;
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
                    cursor: pointer;
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
                font-size: 16px;
            }
            .v-stepper__label {
                margin-top: 8px;
                font-weight: 400;
                color: map-get($colors, 'primary');
                text-shadow: none;
                text-align: center;
            }
        }
    }
}
</style>
