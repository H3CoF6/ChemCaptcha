/* src/components/CaptchaCanvas.tsx */
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiLoader, FiCheckCircle, FiXCircle, FiRefreshCw, FiTarget } from 'react-icons/fi';
import styles from './CaptchaCanvas.module.scss';
import { encryptPayload, decryptPayload } from '@/utils/crypto';

// ... Points 接口保持不变 ...
interface Point { x: number; y: number; id: number; }
interface Props { slug: string; }

export default function CaptchaCanvas({ slug }: Props) {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [markers, setMarkers] = useState<Point[]>([]);
    const [status, setStatus] = useState<'idle' | 'verifying' | 'success' | 'fail'>('idle');
    const [msg, setMsg] = useState('');

    // 使用 useRef 防止闭包陷阱，如果需要的话 (这里主要用 state 即可)

    const loadCaptcha = async () => {
        setLoading(true);
        setMarkers([]);
        setStatus('idle');
        setMsg('');
        try {
            const url = slug === 'random'
                ? '/api/captcha/random?width=800&height=600'
                : `/api/captcha/${slug}/generate?width=800&height=600`;
            const res = await fetch(url);
            const json = await res.json();
            setData(json);
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
        } catch (e) {
            setMsg("连接服务器失败");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { loadCaptcha(); }, [slug]);

    // 点击背景添加标记
    const handleBgClick = (e: React.MouseEvent) => {
        if (status !== 'idle') return;
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        setMarkers(prev => [...prev, { x, y, id: Date.now() }]);
    };

    const removeMarker = (e: React.MouseEvent, id: number) => {
        e.stopPropagation();
        if (status !== 'idle') return;
        setMarkers(prev => prev.filter(m => m.id !== id));
    };

    // 自动刷新逻辑封装
    const autoNext = (delay = 1500) => {
        setTimeout(() => {
            loadCaptcha();
        }, delay);
    };

    const verify = async () => {
        if (!data) return;
        setStatus('verifying');

        try {
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
                setMsg(result.message || "验证通过");
                // 成功 -> 自动下一题
                autoNext(1000);
            } else {
                setStatus('fail');
                setMsg(result.message || "验证失败");
                // 失败 -> 也自动下一题 (符合你的需求)
                autoNext(1500);
            }
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
        } catch (e) {
            setStatus('fail');
            setMsg("系统错误");
            autoNext(1500);
        }
    };

    return (
        <div className={styles.canvasContainer}>
            <div className={styles.header}>
                <h3>{slug.toUpperCase()} 验证</h3>
                {/* 使用图标装饰 Prompt */}
                <p><FiTarget style={{verticalAlign: 'middle', marginRight: 5}}/> {data?.prompt || "正在加载..."}</p>
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
                                    style={{ left: m.x-12, top: m.y-12 }} // 不知道什么bug，一直定位到左下角，暂时这样修一下，我要好好学前端！！！  // todo !!!
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    exit={{ scale: 0 }}
                                    onClick={(e) => removeMarker(e, m.id)}
                                    whileHover={{ scale: 1.2 }}
                                >
                                    {index + 1}
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {/* 结果层 */}
                        <AnimatePresence>
                            {status === 'success' && (
                                <motion.div
                                    className={styles.resultOverlay}
                                    initial={{opacity:0}}
                                    animate={{opacity:1}}
                                    exit={{opacity:0}}
                                >
                                    <FiCheckCircle size={80} color="var(--success-color)" />
                                    <span style={{color: 'var(--success-color)'}}>VERIFIED</span>
                                </motion.div>
                            )}
                            {status === 'fail' && (
                                <motion.div
                                    className={styles.resultOverlay}
                                    initial={{opacity:0}}
                                    animate={{opacity:1}}
                                    exit={{opacity:0}}
                                >
                                    <FiXCircle size={80} color="var(--error-color)" />
                                    <span style={{color: 'var(--error-color)'}}>FAILED</span>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </>
                )}
            </div>

            <div className={styles.footer}>
                <div className={styles.statusText}>{msg}</div>
                <div className={styles.actions}>
                    <button className={styles.btnIcon} onClick={() => loadCaptcha()} title="换一张">
                        <FiRefreshCw />
                    </button>
                    <button
                        className={styles.btnPrimary}
                        onClick={verify}
                        disabled={status !== 'idle' || markers.length === 0}
                    >
                        {status === 'verifying' ? <FiLoader className={styles.spin}/> : '提交验证'}
                    </button>
                </div>
            </div>
        </div>
    );
}