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
                ApiService.sendFile(ev[0]).then((res) => {
                    console.log(res);
                });
            }
        },
    },
};
</script>

<style scoped></style>
