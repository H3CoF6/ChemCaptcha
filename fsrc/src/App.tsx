import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import CaptchaDebugPage from '@/pages/CaptchaDebug';
import CaptchaWidget from '@/components/CaptchaWidget';
import { Button } from "@heroui/react";

function HomePage() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
            <div className="text-center mb-10">
                <h1 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-600">
                    ChemCaptcha
                </h1>
                <p className="text-gray-500">基于化学结构的下一代安全验证系统</p>
            </div>

            {/* 演示区域 */}
            <div className="mb-10">
                <CaptchaWidget
                    width={400}
                    height={300}
                    onSuccess={() => alert("验证通过！")}
                />
            </div>

            <div className="flex gap-4">
                <Link to="/debug">
                    <Button color="secondary" variant="flat">
                        进入开发者调试模式 (Debug)
                    </Button>
                </Link>
                <Button
                    as="a"
                    href="http://127.0.0.1:8000/docs"
                    target="_blank"
                    color="primary"
                    variant="ghost"
                >
                    后端 API 文档
                </Button>
            </div>

            <div className="mt-10 text-xs text-gray-400">
                Production Mode Preview
            </div>
        </div>
    );
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/debug" element={<CaptchaDebugPage />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App