import react from "eslint-plugin-react/configs/recommended.js"
import reactJsx from "eslint-plugin-react/configs/jsx-runtime.js"
import hooks from "eslint-plugin-react-hooks"
import reactRefresh from "eslint-plugin-react-refresh"
import love from "eslint-config-love"
import tsParser from "@typescript-eslint/parser"
import tseslint from 'typescript-eslint'
import eslint from '@eslint/js'

export default [
  love,
  react,
  reactJsx,
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
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
      }
    }
  },
  {
    plugins: {
      'react-refresh': reactRefresh,
      'react-hooks': hooks
    },
    rules: {
      'react-refresh/only-export-components': 'warn',
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn"
    }
  }
]