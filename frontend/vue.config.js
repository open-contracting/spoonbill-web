module.exports = {
    transpileDependencies: ['vuetify'],
    css: {
        extract: {
            // https://github.com/vuetifyjs/vuetify/issues/5271
            ignoreOrder: true,
        },
        loaderOptions: {
            scss: {
                additionalData: `
                    @import '~vuetify/src/styles/settings/_variables';
                    @import '~@/assets/styles/main.scss';
                `,
            },
        },
    },
};
