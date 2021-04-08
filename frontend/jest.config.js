module.exports = {
    preset: '@vue/cli-plugin-unit-jest',
    setupFilesAfterEnv: ['./jest.setup.js'],
    collectCoverage: true,
    collectCoverageFrom: [
        'src/{components,utils,store,views}/**/*.{js,vue}',
        '!**/node_modules/**',
        '!src/views/UploadFile/UploadFileRegistry.vue',
    ],
    coverageThreshold: {
        global: {
            lines: 80,
        },
    },
};
