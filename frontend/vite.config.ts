import react from '@vitejs/plugin-react'
import vike from 'vike/plugin'
import type { UserConfig } from 'vite'

const config: UserConfig = {
  plugins: [react(), vike({ prerender: true })],
  ssr: {
    noExternal: ['styled-components', '@emotion/*']
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    css: true
  }

}

export default config
