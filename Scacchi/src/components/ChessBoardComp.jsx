import { Chessboard } from "react-chessboard";
import { useEffect, useState, useRef } from "react";

export const ChessBoardComp = ({ game, onMakeMove, rotationMode = 'fixed' }) => {
    const [boardWidth, setBoardWidth] = useState(320);
    const boardRef = useRef(null);
    const currentTurn = game.turn(); // 'w' or 'b'
    const position = game.fen();

    useEffect(() => {
        const handleResize = () => {
            setBoardWidth(Math.min(window.innerWidth * 0.9, window.innerHeight * 0.6));
        };

        handleResize();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    // Apply rotation to pieces via DOM manipulation
    useEffect(() => {
        if (!boardRef.current || rotationMode === 'none') return;

        const applyRotation = () => {
            // Get board position to know which pieces are where
            const board = game.board();

            // Find all squares with pieces
            const allSquares = boardRef.current.querySelectorAll('[data-square]');

            allSquares.forEach(square => {
                const squareId = square.getAttribute('data-square');
                if (!squareId) return;

                // Convert square notation (e.g., 'e2') to board array indices
                const file = squareId.charCodeAt(0) - 97; // 'a' = 0, 'b' = 1, etc.
                const rank = 8 - parseInt(squareId[1]); // '8' = 0, '7' = 1, etc.

                const piece = board[rank]?.[file];
                if (!piece) return; // Empty square

                const isBlackPiece = piece.color === 'b';

                // Find SVG in this square
                const svg = square.querySelector('svg');
                if (!svg) return;

                let rotation = '0deg';

                if (rotationMode === 'fixed') {
                    // Fixed: black pieces always 180deg, white pieces 0deg
                    rotation = isBlackPiece ? '180deg' : '0deg';
                } else if (rotationMode === 'dynamic') {
                    // Dynamic: ALL pieces rotate based on turn
                    // White's turn: all pieces 0deg (facing white)
                    // Black's turn: all pieces 180deg (facing black)
                    rotation = currentTurn === 'w' ? '0deg' : '180deg';
                }

                svg.style.transform = `rotate(${rotation})`;
                svg.style.transformOrigin = 'center';
                svg.style.transition = rotationMode === 'dynamic' ? 'none' : 'transform 0.3s ease';
            });
        };

        // Apply rotation with multiple attempts to catch dynamic rendering
        const timeouts = [0, 50, 150].map(delay =>
            setTimeout(applyRotation, delay)
        );

        return () => timeouts.forEach(clearTimeout);
    }, [rotationMode, currentTurn]); // Removed 'position' to prevent flicker on moves

    function onDrop(sourceSquare, targetSquare, piece) {
        return onMakeMove(sourceSquare, targetSquare, piece);
    }

    return (
        <div ref={boardRef} style={{ display: 'flex', justifyContent: 'center' }}>
            <Chessboard
                id="BasicBoard"
                position={position}
                onPieceDrop={onDrop}
                boardWidth={boardWidth}
            />
        </div>
    );
};
