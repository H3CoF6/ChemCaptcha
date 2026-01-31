import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiLoader, FiCheckCircle, FiXCircle, FiRefreshCw } from 'react-icons/fi'; 
import styles from './CaptchaCanvas.module.scss';
import { encryptPayload, decryptPayload } from '@/utils/crypto';

interface Point {
    x: number;
    y: number;
    id: number; // 唯一ID用于删除
}

interface Props {
    slug: string; // 插件标识
}

export default function CaptchaCanvas({ slug }: Props) {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [markers, setMarkers] = useState<Point[]>([]);
    const [status, setStatus] = useState<'idle' | 'verifying' | 'success' | 'fail'>('idle');
    const [msg, setMsg] = useState('');

    // 加载验证码
    const loadCaptcha = async () => {
        setLoading(true);
        setMarkers([]);
        setStatus('idle');
        setMsg('');
        try {
            // 兼容 Random 和 具体 Slug
            const url = slug === 'random'
                ? '/api/captcha/random?width=800&height=600'
                : `/api/captcha/${slug}/generate?width=800&height=600`;

            const res = await fetch(url);
            const json = await res.json();
            setData(json);
        } catch (e) {
            setMsg("连接服务器失败");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { loadCaptcha(); }, [slug]);

    // 点击图片添加标记
    const handleBgClick = (e: React.MouseEvent) => {
        if (status !== 'idle') return;
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        setMarkers(prev => [...prev, { x, y, id: Date.now() }]);
    };

    // 点击标记删除自己
    const removeMarker = (e: React.MouseEvent, id: number) => {
        e.stopPropagation(); // 防止触发背景点击
        if (status !== 'idle') return;
        setMarkers(prev => prev.filter(m => m.id !== id));
    };

    // 验证逻辑 (保持加密)
    const verify = async () => {
        if (!data) return;
        setStatus('verifying');

        try {
            // 转换坐标格式
            const userInput = markers.map(m => ({ x: m.x, y: m.y }));

            const payload = encryptPayload({
                token: data.token,
                user_input: userInput
            });

            const res = await fetch('/api/captcha/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data: payload })
            });

            const resJson = await res.json();
            const result = decryptPayload(resJson.data);

            if (result && result.success) {
                setStatus('success');
                setMsg(result.message);
            } else {
                setStatus('fail');
                setMsg(result.message || "验证失败");
                setTimeout(() => {
                    setStatus('idle');
                    setMarkers([]);
                }, 2000);
            }
        } catch (e) {
            setStatus('fail');
        }
    };

    return (
        <div className={styles.canvasContainer}>
            <div className={styles.header}>
                <h3>{slug.toUpperCase()} 验证</h3>
                <p>{data?.prompt || "正在加载..."}</p>
            </div>

            <div className={styles.stage} style={{ width: 800, height: 600 }}>
                {loading && <div className={styles.loader}><FiLoader className={styles.spin} /></div>}

                {!loading && data && (
                    <>
                        <img
                            src={`data:image/png;base64,${data.img_base64}`}
                            className={styles.captchaImg}
                            onClick={handleBgClick}
                            alt="captcha"
                        />

                        <AnimatePresence>
                            {markers.map((m, index) => (
                                <motion.div
                                    key={m.id}
                                    className={styles.marker}
                                    style={{ left: m.x, top: m.y }}
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    exit={{ scale: 0 }}
                                    onClick={(e) => removeMarker(e, m.id)}
                                    whileHover={{ scale: 1.2, backgroundColor: "var(--error-color)" }}
                                >
                                    {index + 1}
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {/* 结果遮罩 */}
                        {status === 'success' && (
                            <motion.div className={styles.resultOverlay} initial={{opacity:0}} animate={{opacity:1}}>
                                <FiCheckCircle size={60} color="var(--success-color)" />
                                <span>验证通过</span>
                            </motion.div>
                        )}
                        {status === 'fail' && (
                            <motion.div className={styles.resultOverlay} initial={{opacity:0}} animate={{opacity:1}}>
                                <FiXCircle size={60} color="var(--error-color)" />
                                <span>验证失败</span>
                            </motion.div>
                        )}
                    </>
                )}
            </div>

            <div className={styles.footer}>
                <div className={styles.statusText}>{msg}</div>
                <div className={styles.actions}>
                    <button className={styles.btnIcon} onClick={loadCaptcha}><FiRefreshCw /></button>
                    <button
                        className={styles.btnPrimary}
                        onClick={verify}
                        disabled={status !== 'idle' || markers.length === 0}
                    >
                        {status === 'verifying' ? '计算中...' : '提交验证'}
                    </button>
                </div>
            </div>
        </div>
    );
}