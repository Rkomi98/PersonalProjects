import { Chessboard } from "react-chessboard";
import { useEffect, useState } from "react";

export const ChessBoardComp = ({ game, onMakeMove }) => {
    const [boardWidth, setBoardWidth] = useState(320);

    useEffect(() => {
        const handleResize = () => {
            const minDim = Math.min(window.innerWidth, window.innerHeight);
            // Leave space for panels (top and bottom)
            // Assume panels take ~150px each? 
            // Actually landscape vs portrait matters.
            // Prompt implies "same phone/tablet" without rotating device? "senza doverlo girare".
            // Likely portrait mode for two players top/bottom.
            // So width is the constraint usually.
            setBoardWidth(Math.min(window.innerWidth * 0.9, window.innerHeight * 0.6));
        };

        handleResize();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    function onDrop(sourceSquare, targetSquare, piece) {
        return onMakeMove(sourceSquare, targetSquare, piece);
    }

    return (
        <div className="chessboard-wrapper" style={{ display: 'flex', justifyContent: 'center' }}>
            <Chessboard
                id="BasicBoard"
                position={game.fen()}
                onPieceDrop={onDrop}
                boardWidth={boardWidth}
            />
        </div>
    );
};
