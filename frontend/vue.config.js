module.exports = {
    transpileDependencies: ['vuetify'],
    css: {
        loaderOptions: {
            scss: {
                additionalData: `
                    @import "@/assets/styles/_variables.scss";
                    @import '~vuetify/src/styles/settings/_variables';
                `,
            },
        },
    },
};
