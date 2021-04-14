import getQueryParam from '@/utils/getQueryParam';

export default {
    data() {
        return {
            currentTable: null,
            currentTableIndex: 0,
        };
    },

    computed: {
        selections() {
            return this.$store.state.selections;
        },
    },

    async created() {
        const selectionsId = getQueryParam('selections');
        if (selectionsId && !this.selections) {
            await this.$store.dispatch('fetchSelections', selectionsId);
            if (!this.selections) {
                this.$router.push({
                    path: '/upload-file',
                    query: this.$route.query,
                });
                return;
            }
        }
        this.currentTable = this.selections.tables[0];
    },
};
