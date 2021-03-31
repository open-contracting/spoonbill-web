<template>
    <div class="select-data-options">
        <div class="rounded-box select-data-option">
            <h3 class="select-data-option__title">Download OCDS Lite Data</h3>
            <p class="select-data-option__description">
                Skip customization and download the most commonly used fields, as recommended by data analyst at OCP.
            </p>
            <div class="d-flex justify-end">
                <app-button text color="darkest" accent @click="selectOption('AUTO')">
                    <span>Continue with OCDS Lite</span>
                </app-button>
            </div>
        </div>

        <div class="rounded-box select-data-option select-data-option--dark">
            <h3 class="select-data-option__title">Select fields manually</h3>
            <p class="select-data-option__description">
                Explore the dataset to see what fields are available. Download tables to fit your requirements.
            </p>
            <div class="d-flex justify-end">
                <app-button text color="gray-light" accent @click="selectOption('MANUAL')">
                    <span>Continue to select tables</span>
                </app-button>
            </div>
        </div>
    </div>
</template>

<script>
import AppButton from '@/components/App/AppButton';

export default {
    name: 'UploadFileOptions',

    components: { AppButton },

    methods: {
        /**
         * Emits 'select' event with selected option
         * @param { String } option
         * @return { void }
         */
        selectOption(option) {
            this.$emit('select', option);
        },
    },
};
</script>

<style scoped lang="scss">
.select-data-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    column-gap: 36px;
    row-gap: 36px;

    .select-data-option {
        padding: 36px;
        border: 1px solid map-get($colors, 'gray-light');
        background-color: #ffffff;

        &__title {
            margin-bottom: 16px;
            font-size: 1.25em;
            display: inline-block;
            border-bottom: 2px solid transparent;
        }
        &__description {
            padding-bottom: 18px;
            font-weight: 300;
        }

        &--dark {
            background-color: map-get($colors, 'primary');
            color: map-get($colors, 'gray-light');
            border-color: map-get($colors, 'darkest');
            .select-data-option__title {
                color: map-get($colors, 'gray-light');
                border-color: map-get($colors, 'accent');
            }
        }
    }
}
</style>
