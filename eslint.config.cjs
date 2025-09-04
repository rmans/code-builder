const tsPlugin = require('@typescript-eslint/eslint-plugin');
const tsParser = require('@typescript-eslint/parser');
const path = require('path');

module.exports = [
  {
    files: ['**/*.{ts,tsx}'],
    ignores: ['**/*.d.ts', 'node_modules/**', 'builder/cache/**', 'dist/**'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
        project: [path.join(process.cwd(), 'tsconfig.json')],
        tsconfigRootDir: process.cwd()
      }
    },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      'no-throw-literal': 'error',
      '@typescript-eslint/only-throw-error': 'error'
    }
  }
];
