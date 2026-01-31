import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './CaptchaCanvas.module.scss';
import { encryptPayload, decryptPayload } from '@/utils/crypto';
import { FiLoader, FiCheckCircle, FiXCircle, FiRefreshCw, FiTarget, FiMenu, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
interface Point { x: number; y: number; id: number; }
interface Props { slug: string; }

export default function CaptchaCanvas({ slug }: Props) {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [markers, setMarkers] = useState<Point[]>([]);
    const [status, setStatus] = useState<'idle' | 'verifying' | 'success' | 'fail'>('idle');
    const [msg, setMsg] = useState('');

    const [showCatalog, setShowCatalog] = useState(false);
    const [catalogList, setCatalogList] = useState<any[]>([]);
    const [totalItems, setTotalItems] = useState(0);
    const [page, setPage] = useState(1);
    const LIMIT = 20;

    useEffect(() => {
        setShowCatalog(false);
        setPage(1);
        loadCaptcha();
    }, [slug]);


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

    const fetchCatalog = async (pageNum: number) => {
        if (slug === 'random') return;
        try {
            const res = await fetch(`/api/captcha/${slug}/catalog?page=${pageNum}&limit=${LIMIT}`);
            const json = await res.json();
            setCatalogList(json.items);
            setTotalItems(json.total);
            setPage(pageNum);
            setShowCatalog(true);
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
        } catch (e) {
            console.error("Failed to load catalog");
        }
    };

    const loadSpecific = async (path: string) => {
        setLoading(true);
        setMarkers([]);
        setStatus('idle');
        setMsg('');
        setShowCatalog(false); // 选中后关闭目录
        try {
            // 注意：path 需要 encodeURIComponent，因为包含斜杠
            const res = await fetch(`/api/captcha/${slug}/generate_custom?width=800&height=600&path=${encodeURIComponent(path)}`);
            const json = await res.json();
            setData(json);
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
        } catch (e) {
            setMsg("加载指定题目失败");
        } finally {
            setLoading(false);
        }
    };

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
                <div className={styles.headerRow}>
                    {/* 1. 目录按钮：移到左侧 (在 DOM 顺序上放前面虽然不是必须的，但逻辑上清晰) */}
                    {slug !== 'random' && (
                        <button
                            className={styles.catalogBtn}
                            onClick={() => {
                                if (showCatalog) setShowCatalog(false);
                                else fetchCatalog(1);
                            }}
                            title="题库目录"
                        >
                            <FiMenu />
                        </button>
                    )}

                    <h1>{slug.toUpperCase()} 验证</h1>
                </div>
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
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    // --- 添加这一行 ---
                                    style={{ zIndex: 100 }}
                                >
                                    <FiCheckCircle size={80} color="var(--success-color)" />
                                    <span style={{ color: 'var(--success-color)', marginTop: 10, fontWeight: 'bold' }}>VERIFIED</span>
                                </motion.div>
                            )}
                            {status === 'fail' && (
                                <motion.div
                                    className={styles.resultOverlay}
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    // --- 添加这一行 ---
                                    style={{ zIndex: 100 }}
                                >
                                    <FiXCircle size={80} color="var(--error-color)" />
                                    <span style={{ color: 'var(--error-color)', marginTop: 10, fontWeight: 'bold' }}>FAILED</span>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </>
                )}
                {showCatalog && (
                    <div className={styles.catalogOverlay}>
                        <div className={styles.catalogHeader}>
                            <h4>题库目录 ({totalItems})</h4>
                            <button className={styles.closeBtn} onClick={() => setShowCatalog(false)}>
                                <FiXCircle size={20}/>
                            </button>
                        </div>

                        <div className={styles.catalogGrid}>
                            {catalogList.map((item) => {
                                // 3. 核心修改：只获取文件名
                                // 兼容 Windows 反斜杠，统一转为正斜杠后取最后一个元素
                                const fileName = item.path ? item.path.replace(/\\/g, '/').split('/').pop() : 'Unknown';

                                return (
                                    <div
                                        key={item.id}
                                        className={styles.catalogItem}
                                        onClick={() => loadSpecific(item.path)}
                                    >
                                        {/* 显示纯文件名 */}
                                        <span style={{fontWeight: 600}}>{fileName}</span>
                                        <span className={styles.itemId}>ID: {item.id}</span>
                                    </div>
                                );
                            })}
                        </div>

                        {/* 分页控制器 */}
                        <div className={styles.pagination}>
                            <button
                                disabled={page === 1}
                                onClick={() => fetchCatalog(page - 1)}
                                className={styles.btnIcon} // 复用现有按钮样式，或自己写
                                style={{color: 'var(--text-primary)', borderColor: 'var(--glass-border)'}}
                            ><FiChevronLeft/></button>

                            <span>Page {page} / {Math.ceil(totalItems / LIMIT) || 1}</span>

                            <button
                                disabled={page * LIMIT >= totalItems}
                                onClick={() => fetchCatalog(page + 1)}
                                className={styles.btnIcon}
                                style={{color: 'var(--text-primary)', borderColor: 'var(--glass-border)'}}
                            ><FiChevronRight/></button>
                        </div>
                    </div>
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
                        {status === 'verifying' ? <FiLoader className={styles.spin}/> : 'Submit'}
                    </button>
                </div>
            </div>
        </div>
    );
}