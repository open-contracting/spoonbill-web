import getQueryParam from '@/utils/getQueryParam';

export default {
    computed: {
        selections() {
            return this.$store.state.selections;
        },
    },

    methods: {
        async getSelections() {
            const selectionsId = getQueryParam('selections');
            if (selectionsId && !this.selections) {
                await this.$store.dispatch('fetchSelections', selectionsId);
                if (!this.selections) {
                    this.$router.push({
                        name: 'upload file',
                        query: this.$route.query,
                        params: {
                            forced: 'true',
                        },
                    });
                }
            }
        },
    },
};
