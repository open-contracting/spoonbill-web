<template>
    <v-app-bar app color="darkest" height="100" elevation="0">
        <v-container class="d-flex align-center justify-space-between">
            <v-img max-width="175" contain src="@/assets/images/ocp-logo.svg" />
            <div class="lang-selector" style="cursor: pointer">
                <div class="d-flex lang-selector__option">
                    <div tag="div" class="lang" key="sp">{{ getLangNameByCode(currentLanguage).name }}</div>
                    <svg
                        class="ml-2"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            fill-rule="evenodd"
                            clip-rule="evenodd"
                            d="M12 24C18.6274 24 24 18.6274 24 12C24 5.37258 18.6274 0 12 0C5.37258 0 0 5.37258 0 12C0
                            18.6274 5.37258 24 12 24ZM8.27578 6.62068L16.9654 12L8.27578 16.9655V14.069L12.4137
                            12L8.27578 9.51723V6.62068Z"
                        />
                    </svg>
                </div>
                <div class="lang-selector__option lang-selector__option--inactive">
                    <div
                        class="lang mt-2"
                        v-for="language in filteredLanguages"
                        :key="language.name"
                        @click="changeLanguage(language.code)"
                    >
                        {{ language.name }}
                    </div>
                </div>
            </div>
        </v-container>
    </v-app-bar>
</template>

<script>
/* istanbul ignore file */

import Vue from 'vue';

export default {
    name: 'LayoutHeader',
    data() {
        return {
            languages: [
                {
                    code: 'es',
                    name: 'Española',
                },
                {
                    code: 'en_US',
                    name: 'English',
                },
                {
                    code: 'ru',
                    name: 'Русский',
                },
            ],
        };
    },
    computed: {
        isEnglish() {
            return this.$language.current === 'en_US';
        },
        filteredLanguages() {
            return this.languages.filter((l) => l.code !== this.currentLanguage);
        },
        currentLanguage() {
            return this.$language.current;
        },
    },

    methods: {
        changeLanguage(code) {
            Vue.config.language = code;
        },
        getLangNameByCode(code) {
            return this.languages.find((l) => {
                return l.code === code;
            });
        },
    },
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
.lang-selector {
    position: relative;
    min-width: 150px;
    &__option {
        padding: 10px;
        min-width: 150px;

        transition: 0.3s;
        &--inactive {
            display: none;
            left: 0;
            right: 0;
            position: absolute;
            background-color: #fff;
            .lang {
                border-bottom: none;
                color: map-get($colors, 'primary');
            }
        }
        svg {
            transform: rotateZ(90deg);
            path {
                fill: map-get($colors, 'super-light');
            }
        }
    }
    &:hover {
        .lang-selector__option--inactive {
            display: block;
        }
        .lang-selector__option:not(.lang-selector__option--inactive) {
            background-color: map-get($colors, 'accent');
            .lang {
                color: map-get($colors, 'primary');
            }
            svg {
                transform: rotateZ(-90deg);
                path {
                    fill: map-get($colors, 'primary');
                }
            }
        }
    }
}
.lang {
    color: #f8f9fa;
    font-size: 24px;
    font-weight: 500;
    border-bottom: 2px solid map-get($colors, 'accent');
    line-height: 28px;
}
</style>
