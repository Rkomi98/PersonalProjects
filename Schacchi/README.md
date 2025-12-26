# Web Chess - 2 Player Mode

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![Chess.js](https://img.shields.io/badge/chess.js-000000?style=for-the-badge&logo=chess.com&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

A React-based chess application designed for two players sharing a single device (e.g., an iPad or tablet).

## 📋 Project Specifications

| Feature | Details |
| :--- | :--- |
| **React Version** | `^18.2.0` |
| **Build Tool** | Vite `^5.0.8` |
| **Game Engine** | `chess.js` |
| **UI Components** | `react-chessboard` |
| **Logic** | Offline, Local Multiplayer |

## ✨ Key Features

- **Split Screen UI**: Black player controls at the top (rotated 180°), White player at the bottom.
- **Fixed Board**: The board remains centered and does not rotate, suitable for placing the device between players.
- **Material Advantage**: Real-time calculation of material difference (e.g., +3).
- **Optional Chess Clock**: Toggleable 5-minute countdown timer (Blitz style). Timer switches automatically on moves.
- **Legal Moves**: Full chess rules enforcement via `chess.js`.

## 🚀 Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run locally**:
   ```bash
   npm run dev
   ```

## 📦 Deployment to GitHub Pages

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

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
