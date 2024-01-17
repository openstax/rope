module.exports = {
  rules: {
    'react-refresh/only-export-components': 'warn',
    '@typescript-eslint/no-namespace': 'off'
  },
  overrides: [
    {
      files: ['*.ts', '*.tsx'],
      extends: 'standard-with-typescript',
      rules: {
        '@typescript-eslint/space-before-function-paren': [
          'error',
          {
            anonymous: 'always',
            named: 'never',
            asyncArrow: 'always'
          }
        ],
      }
    }
  ],
  reportUnusedDisableDirectives: true,
  ignorePatterns: ['dist/*'],
  env: { browser: true, es2020: true, node: true },
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: 'detect' } },
  plugins: ['react-refresh'],
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'plugin:@typescript-eslint/recommended'
  ],
  parser: '@typescript-eslint/parser'
}
