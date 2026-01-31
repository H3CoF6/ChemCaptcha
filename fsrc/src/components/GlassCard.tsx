/* src/components/GlassCard.tsx */
import { useRef, useState, type CSSProperties, type MouseEvent, type ReactNode } from 'react';
import { motion } from 'framer-motion';
import styles from './GlassCard.module.scss';

interface GlassCardProps {
    children: ReactNode;
    className?: string;
    style?: CSSProperties;
    // 开关是否启用3D光照效果
    enableGlow?: boolean;
}

export default function GlassCard({ children, className = '', style = {}, enableGlow = true }: GlassCardProps) {
    const cardRef = useRef<HTMLDivElement>(null);
    const [cursor, setCursor] = useState({ x: 0, y: 0 });
    const [opacity, setOpacity] = useState(0);

    const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
        if (!cardRef.current || !enableGlow) return;

        const rect = cardRef.current.getBoundingClientRect();
        setCursor({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        });
        setOpacity(1);
    };

    const handleMouseLeave = () => {
        setOpacity(0);
    };

    return (
        <motion.div
            ref={cardRef}
            className={`${styles.card} ${className}`}
            style={style}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
        >
            {/* Spotlight 光效层 */}
            {enableGlow && (
                <div
                    className={styles.spotlight}
                    style={{
                        opacity,
                        background: `radial-gradient(600px circle at ${cursor.x}px ${cursor.y}px, var(--glass-border), transparent 40%)`
                    }}
                />
            )}

            {/* 内容层，确保 z-index 高于光效 */}
            <div className={styles.content}>
                {children}
            </div>
        </motion.div>
    );
}