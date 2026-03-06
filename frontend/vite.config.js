import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte(), basicSsl()],
  server: {
    host: true, // Gör appen tillgänglig på lokala nätverket
    port: 5173
  }
})
