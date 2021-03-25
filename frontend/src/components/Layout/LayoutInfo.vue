<template>
    <div>
        <h1>OCDS Flatten Tool</h1>
        <p class="mb-15">Convert your OCDS JSON data into Excel</p>
        <app-stepper class="mb-8" />
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
