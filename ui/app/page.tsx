"use client";

import React, { useEffect, useState } from "react";

interface MangaResult {
    id: string;
    title: string;
    provider: string;
}

interface Chapter {
    id: string;
    number: string;
    title?: string;
    lang: string;
    provider: string;
}

export default function Home() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<MangaResult[]>([]);
    const [selectedManga, setSelectedManga] = useState<MangaResult | null>(null);
    const [chapters, setChapters] = useState<Chapter[]>([]);
    const [loading, setLoading] = useState(false);
    const [loadingChapters, setLoadingChapters] = useState(false);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query) return;
        setLoading(true);
        try {
            const resp = await fetch(`http://localhost:8000/search/all?q=${encodeURIComponent(query)}`);
            const data = await resp.json();
            setResults(data);
        } catch (err) {
            console.error("Failed to fetch search results:", err);
        } finally {
            setLoading(false);
        }
    };

    const selectManga = async (manga: MangaResult) => {
        setSelectedManga(manga);
        setLoadingChapters(true);
        try {
            const resp = await fetch(`http://localhost:8000/chapters?manga_id=${manga.id}&provider=${manga.provider}`);
            const data = await resp.json();
            setChapters(data);
        } catch (err) {
            console.error("Failed to fetch chapters:", err);
        } finally {
            setLoadingChapters(false);
        }
    };

    if (!mounted) return null;

    return (
        <div className="flex flex-col items-center min-h-screen p-6 md:p-12 overflow-y-auto">
            {/* Background Decorative Element */}
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(0,188,212,0.1),transparent_70%)] pointer-events-none" />

            <header className="w-full max-w-5xl flex justify-between items-center mb-16 relative">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-pink-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                        <span className="font-bold text-white">M</span>
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight">MDex <span className="gradient-text">Singularity</span></h1>
                </div>
                <div className="flex gap-4">
                    <span className="px-3 py-1 glass text-[10px] uppercase tracking-widest text-zinc-400">Kernel v3.5</span>
                    <span className="px-3 py-1 glass text-[10px] uppercase tracking-widest text-cyan-400">Apex Mode</span>
                </div>
            </header>

            <main className="w-full max-w-4xl space-y-12 relative flex-grow">
                {/* Search Section */}
                <section className="space-y-6">
                    <div className="text-center space-y-2">
                        <h2 className="text-4xl font-bold tracking-tight">Explore a Imensidão</h2>
                        <p className="text-zinc-500">Busca universal multi-provedor com tradução inteligente.</p>
                    </div>

                    <form onSubmit={handleSearch} className="relative group max-w-2xl mx-auto">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Digite o título do mangá..."
                            className="w-full h-14 bg-zinc-900/50 border border-zinc-800 focus:border-cyan-500/50 rounded-2xl px-6 outline-none transition-all placeholder:text-zinc-600 glass"
                        />
                        <button
                            disabled={loading}
                            className="absolute right-2 top-2 h-10 px-6 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 transition-all rounded-xl font-semibold text-sm shadow-xl shadow-cyan-900/10"
                        >
                            {loading ? "Buscando..." : "Pesquisar"}
                        </button>
                    </form>
                </section>

                {/* Results Section */}
                {!selectedManga ? (
                    <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {results.map((m) => (
                            <div
                                key={m.id}
                                onClick={() => selectManga(m)}
                                className="glass p-6 group hover:border-cyan-500/30 transition-all cursor-pointer animate-in fade-in slide-in-from-bottom-4"
                            >
                                <div className="mb-4 aspect-[3/4] rounded-lg bg-zinc-800/50 flex items-center justify-center overflow-hidden relative">
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                                    <span className="text-sm font-medium text-zinc-500">Sem Capa</span>
                                    <div className="absolute top-3 left-3 px-2 py-1 bg-black/50 backdrop-blur-md rounded text-[10px] uppercase tracking-wider border border-white/5 text-cyan-400">
                                        {m.provider}
                                    </div>
                                </div>
                                <h3 className="font-semibold text-lg line-clamp-1 group-hover:text-cyan-400 transition-colors uppercase tracking-tight">{m.title}</h3>
                                <p className="text-xs text-zinc-500 mt-1 uppercase tracking-tighter">ID: {m.id.substring(0, 8)}...</p>
                            </div>
                        ))}

                        {!loading && query && results.length === 0 && (
                            <div className="col-span-full py-12 text-center text-zinc-600">
                                Nenhum resultado encontrado.
                            </div>
                        )}
                    </section>
                ) : (
                    /* Chapter Selection Section */
                    <section className="animate-in fade-in slide-in-from-right-8 space-y-6">
                        <button onClick={() => setSelectedManga(null)} className="text-zinc-500 hover:text-white flex items-center gap-2 text-sm transition-colors">
                            <span>← Voltar para busca</span>
                        </button>
                        <div className="flex justify-between items-end">
                            <div>
                                <h2 className="text-3xl font-bold">{selectedManga.title}</h2>
                                <p className="text-cyan-400 text-sm">{selectedManga.provider.toUpperCase()}</p>
                            </div>
                            <button className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-pink-600 rounded-lg font-bold text-sm">Download Selecionados</button>
                        </div>

                        <div className="glass max-h-[500px] overflow-y-auto divide-y divide-white/5">
                            {loadingChapters ? (
                                <div className="p-12 text-center text-zinc-500">Carregando capítulos...</div>
                            ) : (
                                chapters.map((c) => (
                                    <div key={c.id} className="p-4 flex justify-between items-center hover:bg-white/5 transition-colors group">
                                        <div className="flex items-center gap-4">
                                            <input type="checkbox" className="w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-cyan-600 focus:ring-cyan-500" />
                                            <div>
                                                <span className="text-sm font-medium">Capítulo {c.number}</span>
                                                {c.title && <span className="text-zinc-500 text-xs ml-2">- {c.title}</span>}
                                            </div>
                                        </div>
                                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${c.lang === 'en' ? 'bg-yellow-500/10 text-yellow-500' : 'bg-green-500/10 text-green-500'}`}>
                                            {c.lang}
                                        </span>
                                    </div>
                                ))
                            )}
                        </div>
                    </section>
                )}
            </main>

            <footer className="mt-auto py-12 text-[10px] text-zinc-700 uppercase tracking-[0.2em]">
                Design by L0g0rhythm | Built for the Singularity
            </footer>
        </div>
    );
}
