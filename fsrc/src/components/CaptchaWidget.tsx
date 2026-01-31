import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardBody, CardFooter, Button, Spinner } from '@heroui/react';
import { encryptPayload, decryptPayload } from '@/utils/crypto';
import clsx from 'clsx';

interface CaptchaProps {
    slug?: string;
    width?: number;
    height?: number;
    onSuccess?: () => void;
    className?: string;
}

interface Point {
    x: number;
    y: number;
}

export default function CaptchaWidget({
                                          slug,
                                          width = 400,
                                          height = 300,
                                          onSuccess,
                                          className
                                      }: CaptchaProps) {
    const [loading, setLoading] = useState(true);
    const [captchaData, setCaptchaData] = useState<any>(null);
    const [clicks, setClicks] = useState<Point[]>([]);
    const [verifyStatus, setVerifyStatus] = useState<'idle' | 'verifying' | 'success' | 'fail'>('idle');
    const [message, setMessage] = useState('');

    const imgRef = useRef<HTMLImageElement>(null);

    // 获取验证码
    const fetchCaptcha = async () => {
        setLoading(true);
        setClicks([]);
        setVerifyStatus('idle');
        setMessage('');

        try {
            const url = slug
                ? `/api/captcha/${slug}/generate?width=${width}&height=${height}`
                : `/api/captcha/random?width=${width}&height=${height}`; // 生产模式

            const res = await fetch(url);
            const data = await res.json();
            setCaptchaData(data);
        } catch (e) {
            console.log(e);
            setMessage("网络错误，无法加载验证码");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCaptcha();
    }, [slug]);

    // 处理图片点击
    const handleImageClick = (e: React.MouseEvent<HTMLImageElement>) => {
        if (verifyStatus === 'success' || verifyStatus === 'verifying') return;

        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // 添加点击标记
        setClicks(prev => [...prev, { x, y }]);
    };

    // 撤销上一步
    const undo = () => setClicks(prev => prev.slice(0, -1));

    // 提交验证
    const verify = async () => {
        if (!captchaData) return;
        setVerifyStatus('verifying');

        // 1. 构造原始数据对象
        const rawPayload = {
            token: captchaData.token,
            user_input: clicks
        };

        // 2. 全量加密！！
        const encryptedBody = encryptPayload(rawPayload);

        // 具体的 API 调用
        // 注意：现在统一走 /verify 接口，或者你可以让 dev 模式的独立接口也走这个加密逻辑
        // 为了简单，我们让所有验证都走统一加密接口，或者你可以保留 slug 逻辑但 payload 结构要一致
        const verifyUrl = `/api/captcha/verify`;

        try {
            const res = await fetch(verifyUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // 3. 发送加密包裹: {"data": "..."}
                body: JSON.stringify({ data: encryptedBody })
            });

            const responseJson = await res.json();

            // 4. 解密响应: 后端返回的是 { "data": "..." }
            if (responseJson.data) {
                const decryptedResult = decryptPayload(responseJson.data);

                if (decryptedResult && decryptedResult.success) {
                    setVerifyStatus('success');
                    setMessage("验证通过！正在跳转...");
                    setTimeout(() => onSuccess && onSuccess(), 1000);
                } else {
                    setVerifyStatus('fail');
                    setMessage(decryptedResult?.message || "验证失败");
                    setTimeout(() => {
                        setVerifyStatus('idle');
                        setClicks([]);
                    }, 1500);
                }
            } else {
                throw new Error("Invalid response format");
            }

        } catch (e) {
            console.error(e);
            setVerifyStatus('fail');
            setMessage("系统异常或解密失败");
        }
    };

    return (
        <Card className={clsx("backdrop-blur-md bg-white/70 dark:bg-black/60 border-white/20 shadow-xl", className)}>
            <CardBody className="flex flex-col items-center p-4">
                {/* 提示文字 */}
                <div className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-200">
                    {captchaData ? captchaData.prompt : "正在加载安全验证..."}
                </div>

                {/* 图片区域 */}
                <div
                    className="relative rounded-lg overflow-hidden border-2 border-dashed border-gray-300 dark:border-gray-600 transition-colors"
                    style={{ width: width, height: height }}
                >
                    {loading ? (
                        <div className="absolute inset-0 flex items-center justify-center bg-gray-100/50">
                            <Spinner size="lg" />
                        </div>
                    ) : (
                        <>
                            {/* 验证码图片 */}
                            <img
                                ref={imgRef}
                                src={`data:image/png;base64,${captchaData?.img_base64}`}
                                alt="captcha"
                                className="w-full h-full object-contain cursor-crosshair select-none"
                                onClick={handleImageClick}
                                draggable={false}
                            />

                            {/* 点击标记动画 */}
                            <AnimatePresence>
                                {clicks.map((p, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ scale: 0, opacity: 0 }}
                                        animate={{ scale: 1, opacity: 1 }}
                                        exit={{ scale: 0, opacity: 0 }}
                                        className="absolute w-4 h-4 -ml-2 -mt-2 rounded-full bg-primary border-2 border-white shadow-sm pointer-events-none z-10"
                                        style={{ left: p.x, top: p.y }}
                                    />
                                ))}
                            </AnimatePresence>

                            {/* 状态遮罩 */}
                            {verifyStatus === 'success' && (
                                <motion.div
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                    className="absolute inset-0 bg-green-500/30 flex items-center justify-center backdrop-blur-sm"
                                >
                                    <span className="text-4xl">✅</span>
                                </motion.div>
                            )}
                            {verifyStatus === 'fail' && (
                                <motion.div
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                    className="absolute inset-0 bg-red-500/30 flex items-center justify-center backdrop-blur-sm"
                                >
                                    <span className="text-4xl">❌</span>
                                </motion.div>
                            )}
                        </>
                    )}
                </div>
            </CardBody>

            <CardFooter className="justify-between px-4 pb-4 pt-0">
                <Button size="sm" variant="flat" color="warning" onPress={undo} isDisabled={clicks.length === 0 || verifyStatus !== 'idle'}>
                    撤销
                </Button>

                <div className="text-xs text-gray-500">{message}</div>

                <div className="flex gap-2">
                    <Button size="sm" variant="light" onPress={fetchCaptcha}>刷新</Button>
                    <Button
                        size="sm"
                        color="primary"
                        isLoading={verifyStatus === 'verifying'}
                        onPress={verify}
                    >
                        验证
                    </Button>
                </div>
            </CardFooter>
        </Card>
    );
}