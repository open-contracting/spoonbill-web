<template>
    <v-btn v-on="$listeners" v-bind="$attrs">
        <v-img v-if="accent" class="mr-2" src="@/assets/icons/arrow-in-circle--accent.svg" />
        <v-img v-else class="mr-2" src="@/assets/icons/arrow-in-circle.svg" />
        <slot />
    </v-btn>
</template>

<script>
export default {
    name: 'AppButton',

    props: {
        accent: {
            type: Boolean,
            default: false,
        },
    },
};
</script>

<style scoped></style>
