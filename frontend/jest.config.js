module.exports = {
    preset: '@vue/cli-plugin-unit-jest',
    setupFilesAfterEnv: ['./jest.setup.js'],
    collectCoverage: true,
    collectCoverageFrom: ['src/{components,utils,store,views}/**/*.{js,vue}', '!**/node_modules/**'],
    /*coverageThreshold: {
        global: {
            branches: 90,
            functions: 90,
            lines: 90,
        },
    },*/
};
