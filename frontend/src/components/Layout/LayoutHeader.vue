<template>
    <v-app-bar app color="primary" height="120" elevation="0">
        <v-container>
            <router-link to="/select-data">
                <v-img max-width="230" contain src="@/assets/images/ocp-logo.svg" />
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
</style>