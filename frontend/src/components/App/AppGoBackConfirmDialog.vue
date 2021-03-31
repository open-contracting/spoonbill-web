<template>
    <v-dialog v-model="dialog" width="560" persistent>
        <v-card>
            <v-card-text class="pa-0">
                <v-row no-gutters>
                    <v-col cols="1">
                        <v-img height="24" width="24" src="@/assets/icons/back.svg" />
                    </v-col>
                    <v-col cols="11">
                        <h3 class="pt-1 mb-6 card-title">Are you sure to go back?</h3>
                        <p class="card-content">When going to the previous step, all current changes will be reversed</p>
                    </v-col>
                </v-row>
            </v-card-text>

            <v-card-actions class="pa-0 mt-9">
                <v-spacer></v-spacer>
                <v-btn color="gray-light" large @click="cancel">Cancel</v-btn>
                <v-btn class="ml-4" color="accent" large @click="confirm">
                    <v-img class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                    Yes, go back
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
export default {
    name: 'AppGoBackConfirmDialog',

    data() {
        return {
            dialog: false,
            resolve: null,
        };
    },

    created() {
        this.$root.openConfirmGoBackDialog = this.open;
    },

    methods: {
        /**
         * Opens dialog. Returns promise which allows to handle result of dialog closing
         * @return { Promise }
         */
        open() {
            this.dialog = true;

            return new Promise((resolve) => {
                this.resolve = resolve;
            });
        },

        /**
         * Handles click on 'cancel' button. Closes dialog with 'false' result
         */
        cancel() {
            this.resolve(false);
            this.dialog = false;
        },

        /**
         * Handles click on 'confirm' button. Closes dialog with 'true' result
         */
        confirm() {
            this.resolve(true);
            this.dialog = false;
        },
    },
};
</script>

<style scoped lang="scss">
.v-card {
    padding: 36px;
    .card-title {
        font-size: 24px;
        font-weight: 400;
    }
    .card-content {
        font-size: 16px;
        color: map-get($colors, 'primary');
        font-weight: 300;
        line-height: 24px;
    }
}
</style>
