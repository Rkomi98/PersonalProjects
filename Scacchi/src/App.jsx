import { useState, useMemo, useEffect } from 'react'
import './App.css'
import { ChessBoardComp } from './components/ChessBoardComp'
import { PlayerPanel } from './components/PlayerPanel'
import { useChessGame } from './hooks/useChessGame'
import { useChessClock } from './hooks/useChessClock'
import { calculateMaterialAdvantage } from './utils/chessUtils'

function App() {
    const { game, makeMove, status, resetGame: resetChess } = useChessGame();

    // Settings
    const [clockEnabled, setClockEnabled] = useState(false);
    const [initialTime, setInitialTime] = useState(300); // 5 minutes default

    // Clock Hook
    const {
        whiteTime,
        blackTime,
        isRunning,
        startClock,
        stopClock,
        resetClock
    } = useChessClock(initialTime, game.turn(), (loserColor) => {
        alert(`Time's up! ${loserColor === 'w' ? 'White' : 'Black'} lost on time.`);
    });

    // Calculate material
    const { whiteAdvantage, blackAdvantage } = useMemo(() => calculateMaterialAdvantage(game), [game]);

    // Handle move wrapper to handle clock start
    const handleMove = (source, target, piece) => {
        // Prevent moves if game over
        if (status.isGameOver) return false;

        // Make move
        const success = makeMove(source, target, piece);

        if (success) {
            // If clock is enabled and not running, start it (first move of game usually)
            if (clockEnabled && !isRunning && !status.isGameOver) {
                startClock();
            }
        }
        return success;
    };

    const handleReset = () => {
        resetChess();
        resetClock(initialTime);
        // Don't auto start clock
    };

    const toggleClock = () => {
        setClockEnabled(!clockEnabled);
        handleReset();
    };

    // Stop clock on game over
    useEffect(() => {
        if (status.isGameOver) {
            stopClock();
        }
    }, [status.isGameOver, stopClock]);

    // Visual status
    let gameStatusText = "";
    if (status.isCheckmate) gameStatusText = `Checkmate! ${game.turn() === 'w' ? 'Black' : 'White'} wins!`;
    else if (status.isDraw) gameStatusText = "Draw!";
    else if (status.isCheck) gameStatusText = "Check!";

    return (
        <div className="app-container">
            {/* Top Player (Black) - Rotated */}
            <div className="player-section top-player">
                <PlayerPanel
                    name="Black"
                    timer={clockEnabled ? blackTime : 0}
                    isRotated={true}
                    score={blackAdvantage}
                    isActive={!status.isGameOver && game.turn() === 'b'}
                />
            </div>

            {/* Board Area */}
            <div className="board-section">
                <div className="status-overlay">
                    {gameStatusText && <div className="status-badge">{gameStatusText}</div>}
                </div>
                <ChessBoardComp game={game} onMakeMove={handleMove} />
            </div>

            {/* Bottom Player (White) */}
            <div className="player-section bottom-player">
                <PlayerPanel
                    name="White"
                    timer={clockEnabled ? whiteTime : 0}
                    isRotated={false}
                    score={whiteAdvantage}
                    isActive={!status.isGameOver && game.turn() === 'w'}
                />
            </div>

            {/* Controls */}
            <div className="controls">
                <button onClick={handleReset}>New Game</button>
                <button onClick={toggleClock}>
                    {clockEnabled ? "Disable Timer" : "Enable Timer (5m)"}
                </button>
            </div>

            {/* Simple Settings (Optional, minimal for MVP) */}
            <div className="footer-info">
                <p>Two Player Offline Mode</p>
            </div>
        </div>
    )
}

export default App
