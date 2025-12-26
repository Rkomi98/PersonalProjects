# Web Chess - 2 Player Mode

A React-based chess application designed for two players sharing a single device (e.g., an iPad or tablet).

## Features

- **Split Screen UI**: Black player controls at the top (rotated 180°), White player at the bottom.
- **Fixed Board**: The board remains centered and does not rotate, suitable for placing the device between players.
- **Material Advantage**: Real-time calculation of material difference (e.g., +3).
- **Optional Chess Clock**: Toggleable 5-minute countdown timer (Blitz style). Timer switches automatically on moves.
- **Legal Moves**: Full chess rules enforcement via `chess.js`.

## Tech Stack

- **React** (Vite)
- **chess.js** (Game logic)
- **react-chessboard** (Board UI)

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run locally**:
   ```bash
   npm run dev
   ```

## Deploying to GitHub Pages

To make this app available online:

1. **Update `vite.config.js`**:
   Set the base path to your repository name.
   ```javascript
   export default defineConfig({
     plugins: [react()],
     base: '/Schacchi/', // Replace 'Schacchi' with your repo name if different
   })
   ```

2. **Build the project**:
   ```bash
   npm run build
   ```

3. **Deploy**:
   You can manually upload the contents of the `dist` folder to a `gh-pages` branch, or use a tool:

   ```bash
   # Initialize git if not done
   git init
   git add .
   git commit -m "Initial commit"
   
   # Push to GitHub (ensure remote is set)
   # git remote add origin https://github.com/Rkomi98/PersonalProjects.git
   # git push -u origin main

   # Deployment using gh-pages package
   npm install --save-dev gh-pages
   ```

   Add a deploy script to `package.json`:
   ```json
   "scripts": {
     "deploy": "gh-pages -d dist"
   }
   ```

   Then run:
   ```bash
   npm run deploy
   ```

   Alternatively, configure GitHub Actions to deploy from the `dist` folder.

## License

MIT
