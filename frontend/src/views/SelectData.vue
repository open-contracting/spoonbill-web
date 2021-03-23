<template>
    <div class="d-flex justify-center">
        <app-dropzone />
    </div>
</template>

<script>
import AppDropzone from '../components/App/AppDropzone';

export default {
    name: 'SelectData',
    components: { AppDropzone },
};
</script>

<style scoped></style>
