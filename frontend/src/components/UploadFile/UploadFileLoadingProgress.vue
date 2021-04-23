<template>
    <div class="d-flex flex-column justify-center align-center select-data-loading-progress">
        <span class="mb-1">
            {{ status }}
        </span>

        <div class="d-flex w-100">
            <v-img class="mr-4" height="48" max-width="38" contain src="@/assets/icons/json.svg" />

            <div class="py-1 d-flex flex-column w-100">
                <div class="file-name">
                    {{ fileName }}
                </div>
                <v-progress-linear height="7" :indeterminate="percent === -1" :value="percent" :color="color" />
                <div v-show="percent > -1" class="align-self-end">{{ percent }}%</div>
            </div>
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
    padding: 32px 86px;
    width: 100%;
    border: 1px dashed map-get($colors, 'gray-dark');
    border-radius: 8px;
    background-color: #ffffff;

    .file-name {
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
