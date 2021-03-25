<template>
    <div class="d-flex justify-center">
        <app-dropzone @input="onFileSelect" />
    </div>
</template>

<script>
import AppDropzone from '../components/App/AppDropzone';
import ApiService from '@/services/ApiService';

export default {
    name: 'SelectData',

    components: { AppDropzone },

    methods: {
        async onFileSelect(ev) {
            if (ev && ev.length) {
                const formData = new FormData();
                formData.append('file', ev[0]);
                ApiService.sendFile(formData).then((res) => {
                    console.log(res);
                });
            }
        },
    },
};
</script>

<style scoped></style>
