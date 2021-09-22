<template>
    <v-dialog v-model="dialog" width="528px" height="405px">
        <v-card class="dialog-content">
            <v-card-text class="pa-0">
                <v-row no-gutters>
                    <v-col cols="11">
                        <h3 class="pt-1 mb-6 card-title">Not all arrays can be merged</h3>
                        <div class="card-content">
                            <div>
                                It is not possible to merge some arrays as this will make it too large for use in Excel.
                            </div>
                            <div class="options">Options:</div>
                            <div class="radio-wrapper">
                                <v-radio-group v-model="radioGroup">
                                    <v-radio
                                        color="indigo"
                                        v-for="item in radioOptins"
                                        :key="item.value"
                                        :label="item.label"
                                        :value="item.value"
                                    ></v-radio>
                                </v-radio-group>
                            </div>
                        </div>
                    </v-col>
                </v-row>
            </v-card-text>

            <v-card-actions class="pa-0 mt-9">
                <v-spacer></v-spacer>
                <v-btn outlined height="40px" width="88px" class="cancel-btn" @click="dialog = false"> Cancel </v-btn>
                <v-btn height="40px" width="105px" class="save-btn" @click="onContinueClick"> Continue </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
<script>
/* istanbul ignore file */

export default {
    name: 'CustomizeDialog',
    props: {
        isOpen: {
            type: Boolean,
            default: false,
        },
    },
    data: function () {
        return {
            radioGroup: 'keep',
            radioOptins: [
                {
                    value: 'keep',
                    label: 'Keep all tables unmerged and continue',
                },
            ],
        };
    },
    methods: {
        async onContinueClick() {
            if (this.radioGroup === 'remove') {
                this.$emit('onSplitSwitchChange', false);
            }
            this.dialog = false;
        },
    },
    computed: {
        dialog: {
            get() {
                return this.isOpen;
            },
            set(val) {
                this.$emit('setIsDialogOpen', val);
            },
        },
    },
};
</script>
<style scoped lang="scss">
::v-deep .v-dialog {
    background-color: white;
    height: 405px;
}
.v-card {
    padding: 36px;
    height: 100%;
    .card-title {
        font-size: 24px;
        font-weight: 400;
    }
    &__text {
        height: 80%;
    }
    .card-content {
        font-size: 16px;
        color: map-get($colors, 'primary');
        font-weight: 300;
        line-height: 24px;
    }
}
.options {
    margin-top: 10px;
}
.save-btn {
    background-color: indigo !important;
    color: white;
}
.cancel-btn {
    color: indigo;
}
</style>
