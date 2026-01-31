import { useState, useEffect } from 'react';
import CaptchaWidget from '@/components/CaptchaWidget';
import { Listbox, ListboxItem, ScrollShadow } from "@heroui/react";

export default function CaptchaDebugPage() {
    const [plugins, setPlugins] = useState<string[]>([]);
    const [selectedSlug, setSelectedSlug] = useState<string>('');

    // 加载插件列表
    useEffect(() => {
        fetch('/api/captcha/list')
            .then(res => res.json())
            .then(data => {
                setPlugins(data);
                if(data.length > 0) setSelectedSlug(data[0]);
            })
            .catch(err => console.error("Dev mode plugin list failed", err));
    }, []);

    return (
        <div className="flex h-full w-full bg-[url('https://w.wallhaven.cc/full/qz/wallhaven-qz3kwd.jpg')] bg-cover bg-center">
            {/* 左侧栏：插件选择 */}
            <div className="w-64 bg-background/80 backdrop-blur-xl border-r border-divider flex flex-col">
                <div className="p-4 font-bold text-xl border-b border-divider">
                    🧪 实验室
                </div>
                <ScrollShadow className="flex-1 p-2">
                    <Listbox
                        aria-label="Plugins"
                        onAction={(key) => setSelectedSlug(key as string)}
                        selectionMode="single"
                        selectedKeys={[selectedSlug]}
                        variant="flat"
                        color="primary"
                    >
                        {plugins.map(slug => (
                            <ListboxItem key={slug} description={`Slug: ${slug}`}>
                                {slug.toUpperCase()} 插件
                            </ListboxItem>
                        ))}
                    </Listbox>
                </ScrollShadow>
                <div className="p-4 text-xs text-gray-500">
                    Dev Mode Enabled
                </div>
            </div>

            {/* 右侧：展示区域 */}
            <div className="flex-1 flex flex-col items-center justify-center relative">
                <div className="absolute inset-0 bg-black/20 pointer-events-none" /> {/* 遮罩层增加对比度 */}

                <div className="z-10 flex flex-col gap-4 items-center">
                    <h2 className="text-3xl font-bold text-white drop-shadow-md">
                        {selectedSlug.toUpperCase()} CAPTCHA
                    </h2>

                    {/* 这里的 key 很重要，切换 slug 时强制重新渲染组件 */}
                    {selectedSlug && (
                        <CaptchaWidget
                            key={selectedSlug}
                            slug={selectedSlug}
                            width={500}
                            height={400}
                            className="w-[540px]" // 稍微比图片宽一点
                        />
                    )}
                </div>
            </div>
        </div>
    );
}