<template>
    <v-app-bar app color="darkest" height="100" elevation="0">
        <v-container>
            <v-img max-width="175" contain src="@/assets/images/ocp-logo.svg" />
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
