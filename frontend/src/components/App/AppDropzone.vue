<template>
    <div class="d-flex justify-center align-center app-dropzone" @drop="dropHandler" @dragover.prevent>
        <v-img height="48" max-width="48" src="@/assets/icons/drag-n-drop.svg" />

        <div class="ml-4 d-flex flex-column align-center">
            <translate class="mb-4">Drag and drop or click here</translate>

            <div>
                <input type="file" class="d-none" ref="fileInput" @change="onFileSelect" />

                <app-button class="app-btn" large show-icon @click="$refs.fileInput.click()" color="gray-light">
                    <translate>Browse files</translate>
                </app-button>
            </div>
        </div>
    </div>
</template>

<script>
import AppButton from '@/components/App/AppButton';

export default {
    name: 'AppDropzone',

    components: { AppButton },

    methods: {
        /**
         * Handle file select
         * @param { InputEvent } ev
         */
        onFileSelect(ev) {
            if (ev.target.files) {
                this.$emit('input', ev.target.files[0]);
                ev.target.value = null;
            }
        },

        /**
         * Handle file drop
         * @param { DragEvent } ev
         */
        dropHandler(ev) {
            ev.preventDefault();
            this.highlighted = false;

            if (ev.dataTransfer?.files?.length) {
                this.$emit('input', ev.dataTransfer.files[0]);
            }
        },
    },
};
</script>

<style scoped lang="scss">
.app-dropzone {
    padding: 56px;
    width: 100%;
    border: 1px dashed map-get($colors, 'gray-dark');
    border-radius: 8px;
    background-color: #ffffff;
}
</style>
