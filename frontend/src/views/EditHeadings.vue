<template>
    <v-row>
        <v-col cols="12" md="8">
            <translate tag="h2" class="page-title">Add friendly column headings</translate>
        </v-col>

        <v-col cols="12" v-if="$store.state.selections">
            <edit-heading-options @change="changeHeadingsType" />

            <edit-headings-tables :headings-type="$store.state.selections.headings_type" />

            <div class="mt-10 d-flex">
                <v-btn class="mr-6" color="gray-light" x-large @click="onBackClick">
                    <translate>Go back</translate>
                </v-btn>

                <v-btn color="accent" x-large @click="onContinueClick">
                    <v-img class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                    <translate>Continue</translate>
                </v-btn>
            </div>
        </v-col>
    </v-row>
</template>

<script>
import EditHeadingOptions from '@/components/EditHeadings/EditHeadingOptions';
import ApiService from '@/services/ApiService';
import EditHeadingsTables from '@/components/EditHeadings/EditHeadingsTables';
import selectionsMixin from '@/mixins/selectionsMixin';

export default {
    name: 'EditHeadings',

    components: { EditHeadingsTables, EditHeadingOptions },

    mixins: [selectionsMixin],

    async created() {
        await this.getSelections();
    },

    mounted() {
        window.scroll(0, 0);
    },

    methods: {
        /**
         * Go to previous step
         */
        onBackClick() {
            this.$router.push({ path: '/customize-tables', query: this.$route.query });
        },

        /**
         * Go to next step
         */
        onContinueClick() {
            this.$router.push({ path: '/download', query: this.$route.query });
        },

        /**
         * Change headings type of selections
         * @param { string } value
         */
        async changeHeadingsType(value) {
            try {
                await ApiService.changeHeadingsType(
                    this.$store.state.uploadDetails.type + 's',
                    this.$store.state.uploadDetails.id,
                    this.$store.state.selections.id,
                    value
                );
                this.$store.commit('setHeadingsType', value);
            } catch (e) {
                /* istanbul ignore next */
                console.error(e);
            }
        },
    },
};
</script>

<style scoped lang="scss"></style>
