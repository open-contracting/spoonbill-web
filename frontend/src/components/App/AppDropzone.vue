<template>
    <div
        class="d-flex flex-column justify-center align-center pa-10 app-dropzone"
        :class="{ 'm-highlighted': highlighted }"
        @drop="dropHandler"
        @dragover="highlighted = true"
        @dragleave="highlighted = false"
        @dragover.prevent
    >
        <v-icon x-large>mdi-file-upload</v-icon>

        <span class="my-5">Drag and drop a file to upload, or</span>

        <input type="file" class="d-none" ref="fileInput" @change="onFileSelect" />
        <v-btn @click="$refs.fileInput.click()" color="primary">Choose a file</v-btn>
    </div>
</template>

<script>
export default {
    name: 'AppDropzone',

    data() {
        return {
            highlighted: false,
        };
    },

    methods: {
        onFileSelect(ev) {
            console.log(ev);
            if (ev.target.files) {
                this.$emit('input', Array.from(ev.target.files));
                ev.target.value = null;
            }
        },

        dropHandler(ev) {
            ev.preventDefault();
            this.highlighted = false;

            if (ev.dataTransfer?.files?.length) {
                this.$emit('input', Array.from(ev.dataTransfer.files));
            }
        },
    },
};
</script>

<style scoped lang="scss">
.app-dropzone {
    max-width: 400px;
    width: 100%;
    border: 2px dashed gray;
    &.m-highlighted {
        border-color: #1976d2;
    }
}
</style>
