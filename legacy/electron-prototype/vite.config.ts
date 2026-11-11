import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// base: './' é obrigatório para funcionar dentro do Electron (file://)
export default defineConfig({
  plugins: [react()],
  base: "./",
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: { port: 5173 },
});
