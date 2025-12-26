import { useState, useEffect } from 'react';

export function useChessClock(initialTime, activeColor, onTimeout) {
    const [whiteTime, setWhiteTime] = useState(initialTime);
    const [blackTime, setBlackTime] = useState(initialTime);
    const [isRunning, setIsRunning] = useState(false);

    useEffect(() => {
        let interval = null;
        if (isRunning) {
            if (activeColor === 'w' && whiteTime <= 0) {
                onTimeout && onTimeout('w');
                setIsRunning(false);
                return;
            }
            if (activeColor === 'b' && blackTime <= 0) {
                onTimeout && onTimeout('b');
                setIsRunning(false);
                return;
            }

            interval = setInterval(() => {
                if (activeColor === 'w') {
                    setWhiteTime(t => t > 0 ? t - 1 : 0);
                } else {
                    setBlackTime(t => t > 0 ? t - 1 : 0);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isRunning, activeColor, whiteTime, blackTime, onTimeout]);

    const resetClock = (newTime = initialTime) => {
        setIsRunning(false);
        setWhiteTime(newTime);
        setBlackTime(newTime);
    };

    return {
        whiteTime,
        blackTime,
        isRunning,
        startClock: () => setIsRunning(true),
        stopClock: () => setIsRunning(false),
        resetClock
    };
}
