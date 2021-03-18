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
            this.$emit('input', Array.from(ev.target.files));
            ev.target.value = null;
        },

        dropHandler(ev) {
            ev.preventDefault();
            this.highlighted = false;

            const files = [];

            if (ev.dataTransfer.items) {
                for (let i = 0; i < ev.dataTransfer.items.length; i++) {
                    if (ev.dataTransfer.items[i].kind === 'file') {
                        const file = ev.dataTransfer.items[i].getAsFile();
                        files.push(file);
                    }
                }
            } else {
                for (let i = 0; i < ev.dataTransfer.files.length; i++) {
                    const file = ev.dataTransfer.files[i];
                    files.push(file);
                }
            }

            this.$emit('input', files);
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
