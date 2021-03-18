module.exports = {
    preset: '@vue/cli-plugin-unit-jest',
    setupFilesAfterEnv: ['./jest.setup.js'],
    collectCoverage: true,
    collectCoverageFrom: ['src/{components,utils,store,views}/**/*.{js,vue}', '!**/node_modules/**'],
};
