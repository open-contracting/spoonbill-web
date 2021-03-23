module.exports = {
    transpileDependencies: ['vuetify'],
    css: {
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
