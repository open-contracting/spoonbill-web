<template>
    <v-app-bar app color="primary" height="120" elevation="0">
        <v-container>
            <router-link class="d-block" to="/select-data">
                <v-img max-width="230" contain src="@/assets/images/ocp-logo.svg" @click="$store.dispatch('clearDetails')" />
            </router-link>
        </v-container>
    </v-app-bar>
</template>

<script>
export default {
    name: 'LayoutHeader',
};
</script>

<style scoped lang="scss">
::v-deep .v-toolbar__content {
    padding-left: 0;
    padding-right: 0;
}
.router-link-active {
    width: max-content;
}
</style>
