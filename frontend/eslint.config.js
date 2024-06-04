import react from "eslint-plugin-react"
import hooks from "eslint-plugin-react-hooks"
import reactRefresh from "eslint-plugin-react-refresh"
import love from "eslint-config-love"
import tsParser from "@typescript-eslint/parser"
import globals from "globals"

export default [
  love,
  {
    rules: {
      'react-refresh/only-export-components': 'warn',
    }
  },
  {
    files: [
      '**/*.ts',
      '**/*.tsx'
    ],
    rules: {
      '@typescript-eslint/space-before-function-paren': [
        'error',
        {
          anonymous: 'always',
          named: 'never',
          asyncArrow: 'always'
        }
      ],
      'no-undef': 'off'
    }
  },
  {
    ignores: [
      'dist/**',
      'eslint.config.js'
    ]

  },
  {
    linterOptions: {
      reportUnusedDisableDirectives: true
    }
  },
  {
    settings: {
      react: { version: 'detect' }
    }
  },
  {
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest'
      },
      globals: {
        ...globals.browser,
        ...globals.es2020,
        ...globals.node,
      }
    }
  },
  {
    plugins: {
      'react-refresh': reactRefresh,
      'react-hooks': hooks,
      'react': react
    }
  }
]