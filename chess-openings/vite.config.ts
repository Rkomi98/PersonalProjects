import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig(({ command }) => {
  const basePath = command === "build" ? "/PersonalProjects/" : "/";

  return {
    base: basePath,
    optimizeDeps: {
      include: ["react", "react-dom", "react-chessboard", "chess.js"]
    },
    plugins: [
      react(),
      VitePWA({
        registerType: "autoUpdate",
        includeAssets: ["favicon.svg", "pwa-192x192.png", "pwa-512x512.png"],
        manifest: {
          name: "Chess Openings Trainer",
          short_name: "Openings",
          start_url: basePath,
          scope: basePath,
          display: "standalone",
          background_color: "#0b0b0c",
          theme_color: "#0b0b0c",
          icons: [
            {
              src: "pwa-192x192.png",
              sizes: "192x192",
              type: "image/png"
            },
            {
              src: "pwa-512x512.png",
              sizes: "512x512",
              type: "image/png"
            }
          ]
        },
        workbox: {
          navigateFallback: `${basePath}index.html`
        }
      })
    ]
  };
});
