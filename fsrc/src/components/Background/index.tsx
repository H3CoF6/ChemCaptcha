/* src/components/Background/index.tsx */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { GiChemicalDrop, GiTestTubes, GiBubblingFlask, GiAtom } from 'react-icons/gi';
import { TbFlask2 } from 'react-icons/tb';
import { SlChemistry } from "react-icons/sl";
import styles from './Background.module.scss';

// 图标池
const ICONS = [GiChemicalDrop, GiTestTubes, GiBubblingFlask, GiAtom, SlChemistry, TbFlask2];

interface PatternItem {
    id: number;
    x: number;
    y: number;
    size: number;
    rotate: number;
    Icon: unknown;
    delay: number;
}

export default function Background() {
    const [patterns, setPatterns] = useState<PatternItem[]>([]);

    useEffect(() => {
        // 生成随机的化学背景图案
        const count = 15; // 图标数量
        const newPatterns: PatternItem[] = [];
        for (let i = 0; i < count; i++) {
            newPatterns.push({
                id: i,
                x: Math.random() * 100, // %
                y: Math.random() * 100, // %
                size: 30 + Math.random() * 100, // px
                rotate: Math.random() * 360,
                Icon: ICONS[Math.floor(Math.random() * ICONS.length)],
                delay: Math.random() * 5
            });
        }
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setPatterns(newPatterns);
    }, []);

    return (
        <div className={styles.container}>
            {/* 1. 静态/动态光斑 (对应你的 PageBackground 需求) */}
            <div className={`${styles.blob} ${styles.blob1}`} />
            <div className={`${styles.blob} ${styles.blob2}`} />
            <div className={`${styles.blob} ${styles.blob3}`} />

            {/* 2. 化学结构式乱排层 */}
            <div className={styles.patternLayer}>
                {patterns.map((p) => (
                    <motion.div
                        key={p.id}
                        className={styles.iconWrapper}
                        style={{
                            left: `${p.x}%`,
                            top: `${p.y}%`,
                            width: p.size,
                            height: p.size,
                            transform: `rotate(${p.rotate}deg)`,
                        }}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.08 }} // 极低透明度，仅作为纹理
                        transition={{ duration: 1, delay: p.delay }}
                    >
                        <p.Icon size="100%" />
                    </motion.div>
                ))}
            </div>
        </div>
    );
}