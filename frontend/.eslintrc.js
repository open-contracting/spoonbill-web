module.exports = {
    root: true,
    env: {
        node: true,
    },
    extends: ['plugin:vue/essential', 'eslint:recommended', '@vue/prettier'],
    parserOptions: {
        parser: 'babel-eslint',
    },
    rules: {
        'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
        'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
        indent: ['error', 4, { SwitchCase: 1 }],
        'max-len': ['error', { code: 125 }],
        'keyword-spacing': ['error', { after: true, before: true }],
        semi: ['error', 'always'],
        'object-curly-spacing': ['error', 'always'],
        quotes: ['error', 'single', { avoidEscape: true }],
        'comma-dangle': ['error', 'only-multiline'],
    },
    overrides: [
        {
            files: [
                'jest.setup.js',
                '**/__mocks__/*.{j,t}s?(x)',
                '**/__tests__/*.{j,t}s?(x)',
                '**/tests/unit/**/*.spec.{j,t}s?(x)',
            ],
            env: {
                jest: true,
            },
        },
    ],
};
