<template>
    <div class="d-flex flex-column justify-center align-center select-data-loading-progress">
        <slot />
        <v-img height="60" contain src="@/assets/icons/json.svg" />

        <div class="file-name">
            {{ fileName }}
        </div>

        <span class="my-3">
            {{ status }}
        </span>

        <div class="d-flex align-center justify-center progress">
            <v-progress-linear height="9" :indeterminate="percent === -1" :value="percent" :color="color" />
            <div v-if="percent > -1" class="ml-2">{{ percent }}%</div>
        </div>

        <v-btn class="app-btn" :disabled="!cancelable" large @click="$emit('cancel')" color="gray-light">Cancel</v-btn>
    </div>
</template>

<script>
export default {
    name: 'UploadFileLoadingProgress',

    props: {
        cancelable: {
            type: Boolean,
            default: false,
        },
        percent: {
            type: Number,
            default: -1,
        },
        fileName: {
            type: String,
            required: true,
        },
        status: {
            type: String,
            required: true,
        },
        color: {
            type: String,
            default: 'accent',
        },
    },
};
</script>

<style scoped lang="scss">
.select-data-loading-progress {
    padding: 52px;
    width: 100%;
    border: 1px dashed map-get($colors, 'gray-dark');
    border-radius: 8px;
    background-color: #ffffff;

    .file-name {
        margin-top: 5px;
        font-size: 14px;
        font-weight: 300;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 375px;
    }

    .progress {
        margin-bottom: 8px;
        width: 100%;
        .v-progress-linear {
            max-width: 375px;
        }
    }

    .app-btn.v-btn--disabled {
        opacity: 0;
    }
}
</style>
