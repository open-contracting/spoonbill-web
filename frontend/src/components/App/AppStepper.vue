<template>
    <v-stepper>
        <v-stepper alt-labels>
            <v-stepper-header>
                <v-stepper-step step="1">Select data</v-stepper-step>

                <v-divider></v-divider>

                <v-stepper-step step="2">Customize table</v-stepper-step>

                <v-divider></v-divider>

                <v-stepper-step step="3">Edit headings</v-stepper-step>

                <v-divider></v-divider>

                <v-stepper-step step="4">Download</v-stepper-step>
            </v-stepper-header>
        </v-stepper>
    </v-stepper>
</template>

<script>
export default {
    name: 'AppStepper',
};
</script>

<style scoped lang="scss">
::v-deep .v-stepper {
    box-shadow: none !important;
    background-color: map-get($colors, 'super-light') !important;
    .v-stepper__header {
        .v-divider {
            margin: 40px -100px 0;
            border: 1px solid map-get($colors, 'gray-light');
        }
        .v-stepper__step {
            &:first-child {
                padding-left: 0;
            }
            &:last-child {
                padding-right: 0;
            }
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
                        left: -4px;
                        top: -4px;
                        width: 33px;
                        height: 33px;
                        border: 2px solid map-get($colors, 'accent');
                        border-radius: 50%;
                    }
                }
            }
            .v-stepper__step__step {
                margin: 4px 4px 13px;
                width: 25px;
                height: 25px;
                color: map-get($colors, 'primary');
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
