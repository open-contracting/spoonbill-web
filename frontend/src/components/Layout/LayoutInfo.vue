<template>
    <div class="pb-6">
        <translate tag="h1" class="mb-2">OCDS Flatten Tool</translate>
        <translate tag="p" class="mb-5">Convert your OCDS JSON data into Excel</translate>
        <app-stepper v-if="!hideStepper" class="mb-0" />
    </div>
</template>

<script>
import AppStepper from '@/components/App/AppStepper';
/* istanbul ignore file */

export default {
    name: 'LayoutInfo',

    components: { AppStepper },
    computed: {
        hideStepper() {
            return this.$route.meta.hideStepper && this.$store.getters.isFileFromDataRegistry;
        },
    },
};
</script>

<style scoped lang="scss">
.mb-5 {
    font-size: 18px;
}
</style>
