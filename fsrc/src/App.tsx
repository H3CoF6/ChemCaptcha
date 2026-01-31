/* src/App.tsx */
import { useState, useEffect } from 'react';
import { FiBox, FiActivity, FiLayers, FiSun, FiMoon } from 'react-icons/fi'; // 引入日月图标
import styles from './App.module.scss';
import GlassCard from '@/components/GlassCard';
import CaptchaCanvas from '@/components/CaptchaCanvas';
import Background from '@/components/Background';
import './styles/global.scss';

export default function App() {
    const [plugins, setPlugins] = useState<string[]>([]);
    const [activeSlug, setActiveSlug] = useState('random');
    // 主题状态
    const [theme, setTheme] = useState<'light' | 'dark'>('dark');

    useEffect(() => {
        // 设置 data-theme 属性以控制 CSS 变量
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    useEffect(() => {
        fetch('/api/captcha/list')
            .then(res => res.json())
            .then(data => setPlugins(data))
            .catch(() => console.error("Failed to load plugins"));
    }, []);

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };

    return (
        <>
            {/* 1. 新的动态背景 */}
            <Background />

            {/* 2. 内容层 */}
            <div className={styles.layout}>

                {/* 左侧侧边栏 */}
                <GlassCard className={styles.sidebar}>
                    <div className={styles.brand}>
                        <FiActivity className={styles.logoIcon} />
                        <span>ChemCaptcha</span>

                        {/* 放在 brand 右侧的小主题开关 */}
                        <div
                            onClick={toggleTheme}
                            style={{marginLeft: 'auto', cursor: 'pointer', display: 'flex'}}
                            title="切换主题"
                        >
                            {theme === 'dark' ? <FiSun /> : <FiMoon />}
                        </div>
                    </div>

                    <div className={`${styles.menu} scroll-container`}>
                        <div className={styles.sectionTitle}>Discovery</div>
                        <div
                            className={`${styles.menuItem} ${activeSlug === 'random' ? styles.active : ''}`}
                            onClick={() => setActiveSlug('random')}
                        >
                            <FiBox /> Random
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
                    {/* 开启 GlassCard 的 enableGlow */}
                    <GlassCard className={styles.canvasWrapper} enableGlow={true}>
                        <CaptchaCanvas key={activeSlug} slug={activeSlug} />
                    </GlassCard>
                </main>
            </div>
        </>
    );
}