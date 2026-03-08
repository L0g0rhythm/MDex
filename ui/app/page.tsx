"use client";

import { useEffect, useState } from "react";

export default function Home() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return null;

    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center">
            <div className="glass p-12 max-w-2xl w-full space-y-8 animate-in fade-in zoom-in duration-700">
                <h1 className="text-5xl font-bold tracking-tight gradient-text">
                    MDex Singularity
                </h1>
                <p className="text-zinc-400 text-lg">
                    Omni-v5 Architecture | Égide Apex Integrated
                </p>

                <div className="grid grid-cols-2 gap-4 pt-8">
                    <div className="glass p-4 text-left">
                        <h3 className="text-cyan-400 font-semibold mb-2">IA Omni-Reader</h3>
                        <p className="text-sm text-zinc-500">OCR local e Tradução Universal ativos.</p>
                    </div>
                    <div className="glass p-4 text-left">
                        <h3 className="text-pink-400 font-semibold mb-2">Multi-Provedor</h3>
                        <p className="text-sm text-zinc-500">MangaDex e outros navegáveis simultaneamente.</p>
                    </div>
                </div>

                <button className="mt-8 px-8 py-3 bg-cyan-600 hover:bg-cyan-500 transition-all rounded-full font-bold shadow-lg shadow-cyan-900/20 active:scale-95">
                    Iniciar Exploração
                </button>
            </div>

            <footer className="mt-12 text-zinc-600 text-xs tracking-widest uppercase">
                L0g0rhythm Authority Core | Kernel v3.5
            </footer>
        </div>
    );
}
