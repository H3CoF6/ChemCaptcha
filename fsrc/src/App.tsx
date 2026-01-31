import { useState, useEffect } from 'react';
import { FiBox, FiActivity, FiLayers } from 'react-icons/fi';
import styles from './App.module.scss';
import GlassCard from '@/components/GlassCard';
import CaptchaCanvas from '@/components/CaptchaCanvas';
import './styles/global.scss';
import { time } from "framer-motion";

export default function App() {
    const [plugins, setPlugins] = useState<string[]>([]);
    const [activeSlug, setActiveSlug] = useState('random');

    useEffect(() => {
        fetch('/api/captcha/list')
            .then(res => res.json())
            .then(data => setPlugins(data))
            .catch(() => console.error("Failed to load plugins"));
    }, []);

    return (
        <>
            {/* 1. 背景层：独立出来，自闭合，只负责发光 */}
            <div
                className="background-glow"
                style={{'--bg-image-url': `url('https://t.alcy.cc/fj?time=${time.now()}')`} as never}
            />

            {/* 2. 内容层：作为兄弟元素，层级更高，不受模糊影响 */}
            <div className={styles.layout}>

                {/* 左侧侧边栏 */}
                <GlassCard className={styles.sidebar}>
                    <div className={styles.brand}>
                        <FiActivity className={styles.logoIcon} />
                        <span>ChemShield</span>
                    </div>

                    <div className={`${styles.menu} scroll-container`}>
                        <div className={styles.sectionTitle}>Discovery</div>
                        <div
                            className={`${styles.menuItem} ${activeSlug === 'random' ? styles.active : ''}`}
                            onClick={() => setActiveSlug('random')}
                        >
                            <FiBox /> 随机测试 (Random)
                        </div>

                        <div className={styles.sectionTitle}>Modules</div>
                        {plugins.map(slug => (
                            <div
                                key={slug}
                                className={`${styles.menuItem} ${activeSlug === slug ? styles.active : ''}`}
                                onClick={() => setActiveSlug(slug)}
                            >
                                <FiLayers /> {slug.toUpperCase()}
                            </div>
                        ))}
                    </div>
                </GlassCard>

                {/* 右侧主区域 */}
                <main className={styles.mainContent}>
                    <GlassCard className={styles.canvasWrapper}>
                        <CaptchaCanvas key={activeSlug} slug={activeSlug} />
                    </GlassCard>
                </main>
            </div>
        </>
    );
}