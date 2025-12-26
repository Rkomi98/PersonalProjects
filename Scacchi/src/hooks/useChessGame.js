import { useState, useCallback } from 'react';
import { Chess } from 'chess.js';

export function useChessGame() {
    const [game, setGame] = useState(new Chess());
    // We need to force update because internal chess.js state mutation doesn't trigger generic re-renders
    const [fen, setFen] = useState(game.fen());

    const makeMove = useCallback((sourceSquare, targetSquare, piece) => {
        try {
            const move = {
                from: sourceSquare,
                to: targetSquare,
                promotion: 'q', // always promote to queen for simplicity for now
            };

            const result = game.move(move);

            if (result) {
                // Update state with new FEN
                setFen(game.fen());
                // Create a new instance to ensure reference changes if needed, 
                // though strictly not required if we rely on FEN for the board.
                // But for game logic queries, we need the updated instance.
                // Actually chess.js is stateful. We can clone it or just keep it.
                // For safety/reactivity:
                const newGame = new Chess(game.fen());
                setGame(newGame);
                return true;
            }
        } catch (e) {
            return false;
        }
        return false;
    }, [game]);

    const resetGame = useCallback(() => {
        const newGame = new Chess();
        setGame(newGame);
        setFen(newGame.fen());
    }, []);

    const undoMove = useCallback(() => {
        const result = game.undo();
        if (result) {
            setFen(game.fen());
            setGame(new Chess(game.fen()));
            return true;
        }
        return false;
    }, [game]);

    return {
        game,
        fen,
        makeMove,
        resetGame,
        undoMove,
        status: {
            isCheckmate: game.isCheckmate(),
            isDraw: game.isDraw(),
            isCheck: game.isCheck(),
            isGameOver: game.isGameOver(),
            turn: game.turn()
        }
    };
}
