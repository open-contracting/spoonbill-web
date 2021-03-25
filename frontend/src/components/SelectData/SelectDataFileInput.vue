<template>
    <div>
        <div class="mb-4 d-flex options">
            <div
                class="option"
                :class="{ 'option--selected': option.value === selectedOption }"
                v-for="option in options"
                :key="option.value"
                @click="selectedOption = option.value"
                v-ripple
            >
                {{ option.title }}
            </div>
        </div>

        <app-dropzone v-if="selectedOption === 'FILE'" />

        <select-data-url-input v-else />

        <p class="mt-4 warning-message">
            Note that large files may take a while to process. Please be patient. <br />
            <template v-if="selectedOption === 'FILE'">The maximum filesize permitted is 100MB</template>
        </p>
    </div>
</template>

<script>
import AppDropzone from '@/components/App/AppDropzone';
import SelectDataUrlInput from '@/components/SelectData/SelectDataUrlInput';

export default {
    name: 'SelectDataFileInput',

    components: { SelectDataUrlInput, AppDropzone },

    data() {
        return {
            options: [
                {
                    title: 'Upload JSON file',
                    value: 'FILE',
                },
                {
                    title: 'Supply a URL for JSON',
                    value: 'URL',
                },
            ],
            /** @type { 'FILE' | 'URL' }*/
            selectedOption: 'FILE',
        };
    },
};
</script>

<style scoped lang="scss">
.options {
    .option {
        cursor: pointer;
        padding: 12px 34px;
        background-color: map-get($colors, 'gray-light');
        &--selected {
            background-color: map-get($colors, 'primary');
            color: map-get($colors, 'gray-light');
        }
        &:first-child {
            border-radius: 8px 0 0 8px;
        }
        &:last-child {
            border-radius: 0 8px 8px 0;
        }
    }
}
.warning-message {
    font-weight: 300;
    font-size: 14px;
}
</style>
