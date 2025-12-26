import React from 'react';

export const PlayerPanel = ({ name, timer, isRotated, score, isActive }) => {
    const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    };

    return (
        <div
            className={`player-panel ${isActive ? 'active' : ''}`}
            style={{
                transform: isRotated ? 'rotate(180deg)' : 'none',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: '10px',
                backgroundColor: isActive ? 'rgba(100, 108, 255, 0.1)' : 'transparent',
                border: isActive ? '2px solid #646cff' : '2px solid transparent',
                borderRadius: '8px',
                width: '100%',
                boxSizing: 'border-box',
                transition: 'background-color 0.3s, border 0.3s'
            }}
        >
            <div className="player-info" style={{
                display: 'flex',
                justifyContent: 'space-between',
                width: '100%',
                maxWidth: '300px',
                marginBottom: '5px'
            }}>
                <span className="name" style={{ fontWeight: 'bold' }}>{name}</span>
                {score > 0 && <span className="score" style={{ color: '#4ade80' }}>+{score}</span>}
            </div>
            <div className="timer" style={{
                fontSize: '1.5em',
                fontWeight: 'bold',
                fontVariantNumeric: 'tabular-nums'
            }}>
                {formatTime(timer)}
            </div>
        </div>
    );
};
