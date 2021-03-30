<template>
    <div>
        <h1 class="mb-2">OCDS Flatten Tool</h1>
        <p class="mb-5">Convert your OCDS JSON data into Excel</p>
        <app-stepper class="mb-6" />
    </div>
</template>

<script>
import AppStepper from '@/components/App/AppStepper';

export default {
    name: 'LayoutInfo',

    components: { AppStepper },
};
</script>

<style scoped></style>
