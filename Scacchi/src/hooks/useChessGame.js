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

            // Work on a copy to avoid direct state mutation and preserve history
            const gameCopy = new Chess();
            gameCopy.loadPgn(game.pgn());

            const result = gameCopy.move(move);

            if (result) {
                setGame(gameCopy);
                setFen(gameCopy.fen());
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
        const gameCopy = new Chess();
        gameCopy.loadPgn(game.pgn());

        const result = gameCopy.undo();
        if (result) {
            setGame(gameCopy);
            setFen(gameCopy.fen());
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
