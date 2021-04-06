<template>
    <v-form class="d-flex" ref="urlForm">
        <v-textarea v-model="url" :rules="urlRules" outlined rows="3" auto-grow hide-details></v-textarea>
        <v-btn class="ml-4" large color="accent" @click="sendUrl">
            <translate>Submit</translate>
        </v-btn>
    </v-form>
</template>

<script>
export default {
    name: 'UploadFileUrlInput',

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
                this.$emit('submit', this.url);
            }
        },
    },
};
</script>

<style scoped></style>
