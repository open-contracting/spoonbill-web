<template>
    <div class="table" :key="key">
        <v-row>
            <v-col cols="12" md="6">
                <div v-if="aboutThisTable">
                    <translate tag="p" class="mb-2">About this table</translate>
                    <p class="fw-300" v-for="(item, idx) in aboutThisTable" :key="idx">{{ item }}</p>
                    <template v-if="missingData.length">
                        <translate tag="p" class="mb-2">Missing data</translate>
                        <translate
                            tag="p"
                            class="d-inline-block text-link"
                            @click.native="showMissingDataList = !showMissingDataList"
                        >
                            See column headings with missing data
                        </translate>
                        <div class="p-relative overflow-hidden">
                            <transition name="roll-down" mode="in-out">
                                <ul class="missing-data-list" v-if="showMissingDataList">
                                    <li v-for="item in missingData" :key="item">
                                        {{ item }}
                                    </li>
                                </ul>
                            </transition>
                        </div>
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
                        <ul class="app-list" :key="arraysKey">
                            <li v-for="(item, idx) of arrays" :key="idx">{{ item }}</li>
                        </ul>
                    </div>
                </div>
            </v-col>
        </v-row>
        <v-switch
            :input-value="isSplit"
            @click="onSplitValueChange"
            readonly
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
                :parentTable="getParentTable(table)"
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
        <CustomizeDialog
            :parentTableName="table.name"
            :isOpen="isDialogOpen"
            @setIsDialogOpen="setIsDialogOpen"
            @onSplitSwitchChange="onSplitSwitchChange"
            :unmergebleTables="unmergebleTables"
        />
    </div>
</template>

<script>
/* istanbul ignore file */

import ApiService from '@/services/ApiService';
import Papa from 'papaparse';
import AppTable from '@/components/App/AppTable';
import CustomizeDialog from './CustomizeDialog.vue';
export default {
    name: 'CustomizeTablesTable',

    components: { AppTable, CustomizeDialog },

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
            showMissingDataList: false,
            isDialogOpen: false,
            key: 0,
            arraysKey: 0,
            tableArrayInfoText: {},
            none: this.$gettext('There are no arrays in this table'),
            one: this.$gettext('There is one array in this table'),
            two: this.$gettext('There are two arrays in this table'),
            three: this.$gettext('There are three arrays in this table'),
            four: this.$gettext('There are four arrays in this table'),
            five: this.$gettext('There are five arrays in this table'),
        };
    },

    async created() {
        this.onCreated();
    },
    computed: {
        isGoBackAvailable() {
            return this.table.id !== this.$store.state.selections.tables[0].id;
        },

        additionalInfo() {
            return this.$store.state.uploadDetails.available_tables.find((table) => table.name === this.table.name);
        },

        canBeSplit() {
            return this.tables.length >= 1;
        },
        unmergebleTables() {
            return this.tables.filter((table) => table.mergeable === false && table.include);
        },
        isMergeAllowed() {
            return this.unmergebleTables <= 0;
        },

        isSplit: {
            get() {
                return this.$store.state.selections.tables.find((table) => table.id === this.table.id).split;
            },
            async set(val) {
                if (!val) {
                    if (!this.isMergeAllowed) {
                        this.isDialogOpen = true;
                    } else {
                        await this.onSplitSwitchChange(false);
                    }
                } else {
                    await this.onSplitSwitchChange(val);
                }
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
            let translated = this.$ngettext('There is %{ n } array in this table', 'There are %{ n } arrays in this table');
            let arraysCount = Object.keys(this.additionalInfo.arrays).length;
            switch (arraysCount) {
                case 0:
                    translated = this.none;
                    break;
                case 1:
                    translated = this.one;
                    break;
                case 2:
                    translated = this.two;
                    break;
                case 3:
                    translated = this.three;
                    break;
                case 4:
                    translated = this.four;
                    break;
                case 5:
                    translated = this.five;
                    break;
                default:
                    translated = this.$ngettext(
                        'There is %{ n } array in this table',
                        'There are %{ n } arrays in this table'
                    );
            }

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
                let translatedFirstPart =
                    this.$ngettext('There is data for %{ n } of the', 'There is data for %{ n } of the', availableColumns) +
                    ' ';
                let translatedSecondPart = this.$ngettext(
                    '%{ total } columns',
                    '%{ total } columns',
                    this.additionalInfo.available_data.columns.total
                );
                let result =
                    this.$gettextInterpolate(translatedFirstPart, {
                        n: availableColumns,
                    }) +
                    this.$gettextInterpolate(translatedSecondPart, {
                        total: this.additionalInfo.available_data.columns.total,
                    });
                res.push(result);
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
                // this.onCreated();

                this.getTablePreview(v.id);
            },

            immediate: true,
        },
        $route() {
            this.none = this.$gettext('There are no arrays in this table');
            this.one = this.$gettext('There is one array in this table');
            this.two = this.$gettext('There are two arrays in this table');
            this.three = this.$gettext('There are three arrays in this table');
            this.four = this.$gettext('There are four arrays in this table');
            this.five = this.$gettext('There are five arrays in this table');
        },
    },

    methods: {
        onSplitValueChange(val) {
            val = !this.isSplit;

            this.isSplit = val;
        },
        setIsDialogOpen(val) {
            this.isDialogOpen = val;
        },
        async onCreated() {
            if (this.canBeSplit) {
                try {
                    // await this.$store.dispatch('updateSplitStatus', {
                    //     tableId: this.table.id,
                    //     value: true,
                    // });
                    await this.getTablePreview(this.table.id);
                } catch (e) {
                    /* istanbul ignore next */
                    this.$error(e);
                }
            }
        },
        /**
         * Change include status of table
         * @param { Object } table
         */
        isTableHaveChild(table) {
            return this.tables.some((t) => {
                return t.parent === table.name;
            });
        },
        getParentTable(child) {
            return this.tables.find((table) => table.name === child.parent);
        },
        getChildTablesNames(table) {
            let filteredTables = this.tables.filter((t) => {
                return t.parent === table.name;
            });
            let str = '';
            filteredTables.forEach((t, i) => {
                str += i === filteredTables.length - 1 ? ` ${t.name} ` : ` ${t.name},`;
            });

            return {
                tables: filteredTables,
                str,
            };
        },
        async removeTable(table) {
            if (this.isTableHaveChild(table)) {
                const childTables = this.getChildTablesNames(table);
                const confirmed = await this.$root.openConfirmDialog({
                    title: this.$gettext('Are you sure?'),
                    content:
                        this.$gettext('It is not possible to remove only Array table: ') +
                        this.table.name +
                        this.$gettext(' without Sub-array tables.  Additionally, the following Sub-array tables:') +
                        childTables.str +
                        this.$gettext('will be removed.'),
                    submitBtnText: this.$gettext('Yes, remove tables and continue'),
                    icon: require('@/assets/icons/remove.svg'),
                });
                if (confirmed) {
                    await this.changeIncludeStatus(table, false);
                    childTables.tables.map(async (table) => {
                        await this.changeIncludeStatus(table, false);
                        return table;
                    });
                }
            } else {
                const confirmed = await this.$root.openConfirmDialog({
                    title: this.$gettext('Are you sure?'),
                    content: this.$gettext('Removing this table will mean it will not be included in flattened Excel file'),
                    submitBtnText: this.$gettext('Yes, remove table and continue'),
                    icon: require('@/assets/icons/remove.svg'),
                });
                if (confirmed) {
                    await this.changeIncludeStatus(table, false);
                }
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

        async onSplitSwitchChange(value) {
            if (value === false) {
                await this.unmergebleTables.map(async (table) => {
                    return await this.changeIncludeStatus(table, false);
                });
            }
            try {
                await this.$store.dispatch('updateSplitStatus', {
                    tableId: this.table.id,
                    value: value,
                });
                await this.getTablePreview(this.table.id);
            } catch (e) {
                /* istanbul ignore next */
                this.$error(e);
                this.$store.commit('openSnackbar', {
                    color: 'error',
                    text: e,
                });
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
                data.map(async (preview, i) => {
                    const parsed = await Papa.parse(data[i].preview, {
                        skipEmptyLines: true,
                    });
                    return {
                        id: preview.id,
                        name: preview.name,
                        heading: preview.heading,
                        headers: parsed.data[0],
                        data: parsed.data.slice(1),
                        include: true,
                        ...preview,
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
            this.key = this.key + 1;
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

.roll-down-enter-active,
.roll-down-leave-active {
    transition: margin-top 0.2s !important;
}

.roll-down-enter-active {
    transition-timing-function: ease-out;
}

.roll-down-leave-active {
    transition-timing-function: ease-in;
}

.roll-down-enter,
.roll-down-leave-to {
    margin-top: -120px !important;
}

.missing-data-list {
    list-style: none;
    margin: 0;
    padding: 0;
}
</style>
