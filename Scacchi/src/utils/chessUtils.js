export const PIECE_VALUES = {
    p: 1,
    n: 3,
    b: 3,
    r: 5,
    q: 9,
    k: 0
};

export function calculateMaterialAdvantage(game) {
    const board = game.board();
    let whiteScore = 0;
    let blackScore = 0;

    for (let row of board) {
        for (let square of row) {
            if (square) {
                const val = PIECE_VALUES[square.type] || 0;
                if (square.color === 'w') {
                    whiteScore += val;
                } else {
                    blackScore += val;
                }
            }
        }
    }

    const diff = whiteScore - blackScore;
    return {
        whiteAdvantage: diff > 0 ? diff : 0,
        blackAdvantage: diff < 0 ? -diff : 0
    };
}
