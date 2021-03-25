<template>
    <v-form class="d-flex" ref="urlForm">
        <v-textarea v-model="url" :rules="urlRules" outlined height="80" no-resize hide-details></v-textarea>
        <v-btn class="ml-4" large color="accent" @click="sendUrl">Submit</v-btn>
    </v-form>
</template>

<script>
import ApiService from '@/services/ApiService';

export default {
    name: 'SelectDataUrlInput',

    data() {
        return {
            url: null,
            urlRules: [(v) => !!v || 'Field is required'],
        };
    },

    methods: {
        async sendUrl() {
            const valid = this.$refs.urlForm.validate();
            if (valid) {
                try {
                    const { data } = await ApiService.sendUrl(this.url);
                    this.$store.commit('openSnackbar', {
                        color: 'success',
                        text: 'URL was sent. ID: ' + data.id,
                    });
                    this.$emit('send', data);
                } catch (e) {
                    console.error(e);
                    if (e.response?.data?.detail) {
                        this.$store.commit('openSnackbar', {
                            color: 'error',
                            text: e.response.data.detail,
                        });
                    }
                }
            }
        },
    },
};
</script>

<style scoped></style>
