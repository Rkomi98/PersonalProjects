// Minimal PWA registration (offline cache)
// Requires vite-plugin-pwa
import { registerSW } from "virtual:pwa-register";

registerSW({ immediate: true });
