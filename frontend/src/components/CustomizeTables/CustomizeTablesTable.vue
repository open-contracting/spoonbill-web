<template>
    <div class="table">
        <v-row>
            <v-col cols="12" md="6">
                <div v-if="aboutThisTable">
                    <translate tag="p" class="mb-2">About this table</translate>
                    <p class="fw-300" v-for="(item, idx) in aboutThisTable" :key="idx">{{ item }}</p>
                    <template v-if="missingData.length">
                        <translate tag="p" class="mb-2">Missing data</translate>
                        <v-menu
                            v-model="missingDataMenu"
                            content-class="missing-columns-menu"
                            :close-on-content-click="false"
                        >
                            <template v-slot:activator="{ on, attrs }">
                                <translate tag="p" class="d-inline-block text-link" v-bind="attrs" v-on="on">
                                    See column headings with missing data
                                </translate>
                            </template>
                            <v-card class="pa-4 d-flex">
                                <div class="mr-2 missing-columns-list">
                                    <span v-for="heading in missingData" class="missing-columns-list__item" :key="heading">
                                        {{ heading }}
                                    </span>
                                </div>
                                <v-btn icon color="darkest" @click="missingDataMenu = false">
                                    <v-icon>mdi-close</v-icon>
                                </v-btn>
                            </v-card>
                        </v-menu>
                    </template>
                </div>
            </v-col>

            <v-col cols="12" md="6">
                <div class="table-info">
                    <div v-if="availableData.length">
                        <translate tag="p" class="mb-2">Available data</translate>
                        <ul class="app-list">
                            <li v-for="(item, idx) of availableData" :key="idx">{{ item }}</li>
                        </ul>
                    </div>

                    <div class="mt-4" v-if="arrays.length">
                        <translate tag="p" class="mb-2">Arrays</translate>
                        <ul class="app-list">
                            <li v-for="(item, idx) of arrays" :key="idx">{{ item }}</li>
                        </ul>
                    </div>
                </div>
            </v-col>
        </v-row>
        <v-switch
            v-model="isSplit"
            v-if="canBeSplit && table.include"
            inset
            hide-details
            color="darkest"
            slot="actions"
            :label="isSplit ? $gettext('Keep arrays in main table') : $gettext('Split arrays into separate tables')"
        ></v-switch>
        <v-skeleton-loader class="mt-8" v-if="loading" type="table-tbody"></v-skeleton-loader>
        <div class="mt-8 tables container--full-width" v-if="table.include">
            <app-table
                v-for="(table, idx) in tables"
                :key="table.name"
                :headers="table.headers"
                :name="table.heading || table.name"
                :data="table.data"
                :include="table.include"
                :allow-actions="idx !== 0"
                :additional-columns="additionalColumns"
                highlight-name
                @remove="removeTable(table)"
                @restore="changeIncludeStatus(table, true)"
            />
        </div>
        <app-table
            class="mt-8"
            v-else-if="tables[0]"
            :headers="tables[0].headers"
            :name="tables[0].heading || tables[0].name"
            :data="tables[0].data"
            :include="false"
            highlight-name
        />
        <div class="mt-10 d-flex">
            <v-btn class="mr-6" color="gray-light" x-large @click="$emit('back')" v-if="isGoBackAvailable">
                <translate>Go back</translate>
            </v-btn>

            <v-btn class="mr-6" color="accent" x-large v-if="isInclude" @click="removeMainTable()" key="remove">
                <v-img height="24" width="24" class="mr-2" src="@/assets/icons/remove.svg" />
                <translate>Remove table</translate>
            </v-btn>

            <v-btn class="mr-6" color="accent" x-large v-else @click="changeIncludeStatus(table, true)" key="restore">
                <v-img height="24" width="24" class="mr-2" src="@/assets/icons/restore.svg" />
                <translate>Restore table</translate>
            </v-btn>

            <v-btn color="accent" x-large @click="$emit('save')">
                <v-img class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
                <translate>Save and Continue</translate>
            </v-btn>
        </div>
    </div>
</template>

<script>
import ApiService from '@/services/ApiService';
import Papa from 'papaparse';
import AppTable from '@/components/App/AppTable';

export default {
    name: 'CustomizeTablesTable',

    components: { AppTable },

    props: {
        table: {
            type: Object,
            required: true,
        },
    },

    data() {
        return {
            loading: false,
            tables: [],
            missingDataMenu: false,
        };
    },

    computed: {
        isGoBackAvailable() {
            return this.table.id !== this.$store.state.selections.tables[0].id;
        },

        additionalInfo() {
            return this.$store.state.uploadDetails.available_tables.find((table) => table.name === this.table.name);
        },

        canBeSplit() {
            return Object.values(this.additionalInfo.arrays).some((value) => value >= 5);
        },

        isSplit: {
            get() {
                return this.$store.state.selections.tables.find((table) => table.id === this.table.id).split;
            },
            async set() {
                await this.onSplitSwitchChange();
            },
        },

        isInclude() {
            return this.$store.state.selections.tables.find((table) => table.id === this.table.id).include;
        },

        aboutThisTable() {
            const name = this.table.name;
            /* istanbul ignore next */
            switch (name) {
                case 'awards':
                    return [
                        this.$gettext('This table contains information from the award phase of the contracting process.'),
                        this.$gettext(
                            'There can be more than one award per contracting process e.g. because the ' +
                                'contract is split among different providers, or because it is a standing offer.'
                        ),
                    ];
                case 'parties':
                    return [
                        this.$gettext(
                            'This table contains information on the parties (organizations, economic ' +
                                'operators and other participants) who are involved in the contracting process ' +
                                'and their roles, e.g. buyer, procuring entity, supplier, etc.'
                        ),
                        this.$gettext(
                            'Organization references elsewhere in the data refer back to the entries in this list.'
                        ),
                    ];
                case 'planning':
                    return [
                        this.$gettext('This table contains information from the planning phase of the contracting process.'),
                        this.$gettext(
                            'This includes information related to the process of deciding what to contract, when, and how.'
                        ),
                    ];
                case 'tenders':
                    return [
                        this.$gettext(
                            'This table contains information on the activities undertaken in order ' +
                                'to enter into a contract.'
                        ),
                        this.$gettext(
                            'Data regarding tender process - publicly inviting prospective contractors ' +
                                'to submit bids for evaluation and selecting a winner or winners.'
                        ),
                    ];
                case 'contracts':
                    return [
                        this.$gettext(
                            'This table contains information from the contract creation phase of the ' +
                                'procurement process and the signed contract between the buyer or procuring ' +
                                'entity and supplier(s).'
                        ),
                    ];
                case 'milestones':
                    return [
                        this.$gettext(
                            'This table contains a list of milestones associated with the different stages ' +
                                'of the procurement process (planning, tender, award, contract, implementation).'
                        ),
                    ];
                case 'amendments':
                    return [
                        this.$gettext(
                            'This table contains information on the changes to the different stages of ' +
                                'the procurement process (tender, award, contract). For example, ' +
                                'when the value or duration of a contract is changed. '
                        ),
                        this.$gettext(
                            'The term amendment often has a specific legal ' +
                                'meaning for a publisher. Certain changes to a tender, award, or contract ' +
                                'might only be allowed as part of an amendment.'
                        ),
                    ];
                case 'documents':
                    return [
                        this.$gettext(
                            'This table contains information on the documents available for the different ' +
                                'stages of the procurement process (planning, tender, award, contract, implementation).'
                        ),
                    ];
                default:
                    return null;
            }
        },

        arrays() {
            let translated = this.$ngettext(
                'There is %{ n } array in this tables',
                'There are %{ n } arrays in this tables',
                Object.keys(this.additionalInfo.arrays).length
            );
            return [this.$gettextInterpolate(translated, { n: Object.keys(this.additionalInfo.arrays).length })];
        },

        missingData() {
            return this.additionalInfo?.available_data?.columns?.missing_data || [];
        },

        additionalColumns() {
            return this.additionalInfo.available_data?.columns?.additional || [];
        },

        availableData() {
            const res = [];
            const availableColumns = this.additionalInfo.available_data?.columns?.available;
            if (availableColumns) {
                let translated = this.$ngettext(
                    'There is data for %{ n } column of the ',
                    'There are data for %{ n } of columns of the ',
                    availableColumns
                );
                res.push(
                    this.$gettextInterpolate(translated, { n: availableColumns }) +
                        this.additionalInfo.available_data.columns.total
                );
            }
            const additionalColumns = this.additionalInfo.available_data?.columns?.additional;
            if (additionalColumns?.length) {
                let translated = this.$ngettext(
                    'There is %{ n } column with additional data not part of OCDS',
                    'There are %{ n } columns with additional data not part of OCDS',
                    additionalColumns.length
                );
                res.push(this.$gettextInterpolate(translated, { n: additionalColumns.length }));
                res.push(
                    additionalColumns.length === 1
                        ? this.$gettext('This column is highlighted in violet')
                        : this.$gettext('These columns are highlighted in violet')
                );
            }
            return res;
        },
    },

    watch: {
        table: {
            handler(v) {
                this.getTablePreview(v.id);
            },
            immediate: true,
        },
    },

    methods: {
        /**
         * Change include status of table
         * @param { Object } table
         */
        async removeTable(table) {
            const confirmed = await this.$root.openConfirmDialog({
                title: this.$gettext('Are you sure?'),
                content: this.$gettext('Removing this table will mean it will not be included in flattened Excel file'),
                submitBtnText: this.$gettext('Yes, remove table and continue'),
                icon: require('@/assets/icons/remove.svg'),
            });
            if (confirmed) {
                await this.changeIncludeStatus(table, false);
            }
        },

        /**
         * Change include status of main table
         */
        async removeMainTable() {
            const isLast = this.$store.state.selections.tables
                .filter((table) => table.id !== this.table.id)
                .every((table) => !table.include);
            if (isLast) {
                const confirmed = await this.$root.openConfirmDialog({
                    content:
                        this.$gettext('You cannot remove all of the tables. If you want to remove ') +
                        this.table.name +
                        this.$gettext(' then please restore one of the other tables or re-select available tables.'),
                    submitBtnText: this.$gettext('Re-select available tables'),
                    icon: require('@/assets/icons/remove.svg'),
                });
                if (confirmed) {
                    await this.$router.push({
                        name: 'select data',
                        query: this.$route.query,
                        params: {
                            forced: true,
                        },
                    });
                }
            } else {
                await this.removeTable(this.table);
            }
        },

        async onSplitSwitchChange() {
            try {
                await this.$store.dispatch('updateSplitStatus', {
                    tableId: this.table.id,
                    value: !this.isSplit,
                });
                await this.getTablePreview(this.table.id);
            } catch (e) {
                /* istanbul ignore next */
                this.$error(e);
            }
        },

        /**
         * Fetch and parse preview of table
         * @param { string } tableId
         */
        async getTablePreview(tableId) {
            window.scroll(0, 0);
            this.loading = true;
            const { uploadDetails, selections } = this.$store.state;
            const { data } = await ApiService.getTablePreview(
                uploadDetails.type + 's',
                uploadDetails.id,
                selections.id,
                tableId
            );
            this.tables = await Promise.all(
                data.map(async (preview) => {
                    const parsed = await Papa.parse(data[0].preview, {
                        skipEmptyLines: true,
                    });
                    return {
                        id: preview.id,
                        name: preview.name,
                        heading: preview.heading,
                        headers: parsed.data[0],
                        data: parsed.data.slice(1),
                        include: true,
                    };
                })
            );
            this.loading = false;
        },

        /**
         * Change include status of table
         * @param { Object } table
         * @param { boolean } value
         */
        async changeIncludeStatus(table, value) {
            try {
                await ApiService.changeIncludeStatus(
                    this.$store.state.uploadDetails.type + 's',
                    this.$store.state.uploadDetails.id,
                    this.$store.state.selections.id,
                    table.id,
                    value
                );
                table.include = value;
            } catch (e) {
                /* istanbul ignore next */
                this.$error(e);
            }
        },
    },
};
</script>

<style scoped lang="scss">
.table-name {
    color: map-get($colors, 'moody-blue');
    font-weight: 700;
}
.tables {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}
.missing-columns-menu .v-btn {
    margin-top: -14px;
}

.missing-columns-list {
    display: flex;
    flex-wrap: wrap;
    column-gap: 10px;
    row-gap: 11px;
    &__item {
        padding: 3px 4px;
        background-color: #ffdede;
        font-size: 14px;
    }
}
</style>
