<template>
    <v-row>
        <v-col cols="12" md="8">
            <v-row class="edit-headings-options">
                <v-col cols="12" md="8">
                    <translate tag="p" class="fw-300 mb-6">
                        To make the data easier to work with you can apply user friendly or R friendly headings in English or
                        Spanish to OCDS fields. The original OCDS headings are kept and can be removed in Excel.
                    </translate>
                    <translate tag="p" class="fw-300">
                        Any columns in the dataset that are not OCDS fields will not have any friendly headings applied to
                        them.
                    </translate>
                    <div>
                        <v-radio-group v-model="headingsType">
                            <v-radio
                                v-for="headingsType in headingsTypes"
                                :key="headingsType.value"
                                :label="headingsType.label"
                                :value="headingsType.value"
                            ></v-radio>
                        </v-radio-group>
                    </div>
                </v-col>

                <v-col cols="12">
                    <v-btn color="accent" x-large :disabled="!canApply" @click="$emit('change', headingsType)">
                        <v-img width="24" height="24" class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                        <translate>Apply change</translate>
                    </v-btn>
                </v-col>
            </v-row>
        </v-col>

        <v-col cols="12" md="4">
            <app-f-a-q>
                <translate slot="title">FAQ</translate>

                <v-expansion-panels :value="[0]" accordion multiple>
                    <v-expansion-panel>
                        <v-expansion-panel-header class="d-flex">{{ faqItem.title }}</v-expansion-panel-header>
                        <v-expansion-panel-content>
                            {{ faqItem.content }}
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                </v-expansion-panels>
            </app-f-a-q>
        </v-col>
    </v-row>
</template>

<script>
import AppFAQ from '@/components/App/AppFAQ';

export default {
    name: 'EditHeadingOptions',
    components: { AppFAQ },

    data() {
        return {
            headingsType: this.$store.state.selections.headings_type,
            faqItem: {
                title: this.$gettext('What are R friendly headings?'),
                content: this.$gettext(
                    'R is a coding language that is used for data visualization, statistical analysis and data science.' +
                        'Users that work with R prefer to have the column headings to be provided in a' +
                        'certain way so that the manual work to make the data ready for analysis is reduced.'
                ),
            },
        };
    },

    computed: {
        canApply() {
            return this.$store.state.selections.headings_type !== this.headingsType;
        },

        headingsTypes() {
            return [
                {
                    label: this.$gettext('OCDS headings only'),
                    value: 'ocds',
                },
                {
                    label: this.$gettext('English user friendly headings to all tables'),
                    value: 'en_user_friendly',
                },
                {
                    label: this.$gettext('English R friendly headings to all tables'),
                    value: 'en_r_friendly',
                },
                {
                    label: this.$gettext('Spanish user friendly headings to all tables'),
                    value: 'es_user_friendly',
                },
                {
                    label: this.$gettext('Spanish R friendly headings to all tables'),
                    value: 'es_r_friendly',
                },
            ];
        },
    },
};
</script>

<style scoped lang="scss">
.edit-headings-options {
    padding: 24px;
    border-radius: 4px;
    border: 1px solid map-get($colors, 'gray-dark');
}
</style>
