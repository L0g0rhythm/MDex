'use client'

import { useState, useEffect, useRef } from 'react'
import { Search, Download, BookOpen, CheckCircle2, AlertCircle, Loader2, ChevronRight, LayoutGrid } from 'lucide-react'

export default function Home() {
  const [query, setQuery] = useState('')
  const [mangas, setMangas] = useState<any[]>([])
  const [selectedManga, setSelectedManga] = useState<any>(null)
  const [chapters, setChapters] = useState<any[]>([])
  const [selectedChapterIds, setSelectedChapterIds] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState<{ [key: string]: number }>({})
  const [logs, setLogs] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    connectWS()
    return () => ws.current?.close()
  }, [])

  const connectWS = () => {
    const socket = new WebSocket('ws://localhost:8000/api/v1/ws/progress')
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'progress') {
        setProgress(prev => ({ ...prev, [data.chapter_id]: data.percentage }))
      } else if (data.type === 'log') {
        setLogs(prev => [data.message, ...prev].slice(0, 50))
      }
    }
    socket.onclose = () => setTimeout(connectWS, 3000)
    ws.current = socket
  }

  const searchManga = async () => {
    if (!query) return
    setLoading(true)
    setError(null)
    setMangas([])
    setSelectedManga(null)
    setChapters([])
    
    try {
      const resp = await fetch(`http://localhost:8000/api/v1/manga/search?title=${encodeURIComponent(query)}`)
      const data = await resp.json()
      if (data.error) throw new Error(data.error)
      setMangas(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getChapters = async (manga: any) => {
    setSelectedManga(manga)
    setLoading(true)
    setChapters([])
    try {
      const resp = await fetch(`http://localhost:8000/api/v1/manga/${manga.id}/chapters`)
      const data = await resp.json()
      setChapters(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const startDownload = async () => {
    if (selectedChapterIds.length === 0) return
    setError(null)
    setSuccess(null)
    try {
      const resp = await fetch('http://localhost:8000/api/v1/download/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          manga_id: selectedManga.id,
          chapter_ids: selectedChapterIds
        })
      })
      const data = await resp.json()
      setSuccess(data.message)
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <main className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row items-center justify-between gap-6 animate-fade-in">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 glass rounded-xl flex items-center justify-center pulse-neon">
            <LayoutGrid className="text-[#00f2ff] w-6 h-6" />
          </div>
          <h1 className="text-4xl font-black tracking-tighter neon-cyan">MDEX <span className="text-[#ff00cc]">SINGULARITY</span></h1>
        </div>
        
        <div className="relative w-full md:w-96 group">
          <input 
            type="text" 
            placeholder="Search manga..." 
            className="w-full h-12 pl-12 pr-4 glass rounded-full focus:outline-none focus:ring-2 focus:ring-[#00f2ff] transition-all"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && searchManga()}
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-[#00f2ff] transition-colors" size={20} />
          <button 
            onClick={searchManga}
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-[#00f2ff] text-black px-4 py-1.5 rounded-full font-bold text-sm hover:scale-105 active:scale-95 transition-all"
          >
            {loading ? <Loader2 className="animate-spin" size={16} /> : 'SEARCH'}
          </button>
        </div>
      </header>

      {/* Notifications */}
      <div className="space-y-4">
        {error && (
          <div className="glass border-l-4 border-red-500 p-4 flex items-center gap-3 animate-fade-in">
            <AlertCircle className="text-red-500" />
            <span className="text-red-200">{error}</span>
          </div>
        )}
        {success && (
          <div className="glass border-l-4 border-[#00f2ff] p-4 flex items-center gap-3 animate-fade-in">
            <CheckCircle2 className="text-[#00f2ff]" />
            <span className="text-cyan-100">{success}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Results/Chapters */}
        <div className="lg:col-span-8 space-y-6">
          {!selectedManga ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {mangas.map((manga, i) => (
                <div 
                  key={manga.id} 
                  className="glass group cursor-pointer hover:glass-active transition-all p-4 rounded-2xl flex flex-col gap-4 animate-fade-in"
                  style={{ animationDelay: `${i * 0.05}s` }}
                  onClick={() => getChapters(manga)}
                >
                  <div className="aspect-[3/4] rounded-lg overflow-hidden relative">
                    <img 
                      src={`http://localhost:8000/api/v1/manga/proxy/cover?url=${encodeURIComponent(manga.cover || '')}`} 
                      alt={manga.title} 
                      className="object-cover w-full h-full group-hover:scale-110 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex items-end p-3">
                      <p className="font-bold text-sm line-clamp-2">{manga.title}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass rounded-3xl p-6 space-y-6 animate-fade-in">
              <div className="flex items-center justify-between">
                <button 
                  onClick={() => setSelectedManga(null)}
                  className="text-sm text-gray-400 hover:text-[#00f2ff] flex items-center gap-1"
                >
                  <ChevronRight className="rotate-180" size={16} /> Back to results
                </button>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-400">{selectedChapterIds.length} selected</span>
                  <button 
                    onClick={startDownload}
                    className="bg-[#ff00cc] text-white px-6 py-2 rounded-full font-bold flex items-center gap-2 hover:scale-105 active:scale-95 transition-all shadow-[0_0_15px_rgba(255,0,204,0.4)]"
                  >
                    <Download size={18} /> DOWNLOAD
                  </button>
                </div>
              </div>

              <div className="flex gap-6 items-start">
                <img 
                  src={`http://localhost:8000/api/v1/manga/proxy/cover?url=${encodeURIComponent(selectedManga.cover || '')}`} 
                  className="w-32 h-44 object-cover rounded-xl shadow-2xl" 
                  alt="" 
                />
                <div>
                  <h2 className="text-2xl font-bold neon-cyan mb-2">{selectedManga.title}</h2>
                  <p className="text-gray-400 text-sm line-clamp-4">{selectedManga.description}</p>
                </div>
              </div>

              <div className="max-h-[500px] overflow-y-auto pr-2 space-y-2">
                {chapters.map((chap) => (
                  <label 
                    key={chap.id} 
                    className={`flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all ${
                      selectedChapterIds.includes(chap.id) ? 'bg-[#00f2ff]/10 border border-[#00f2ff]/30' : 'hover:bg-white/5 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <input 
                        type="checkbox" 
                        className="w-5 h-5 accent-[#00f2ff]"
                        checked={selectedChapterIds.includes(chap.id)}
                        onChange={(e) => {
                          if (e.target.checked) setSelectedChapterIds(prev => [...prev, chap.id])
                          else setSelectedChapterIds(prev => prev.filter(id => id !== chap.id))
                        }}
                      />
                      <div>
                        <p className="font-bold">Chapter {chap.chapter}</p>
                        <p className="text-xs text-gray-400">{chap.title || 'No Title'}</p>
                      </div>
                    </div>
                    {progress[chap.id] !== undefined && (
                      <div className="flex items-center gap-3">
                        <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-[#00f2ff] transition-all duration-300" 
                            style={{ width: `${progress[chap.id]}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono">{progress[chap.id]}%</span>
                      </div>
                    )}
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Console/Status */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass rounded-3xl p-6 h-[400px] flex flex-col animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center gap-2 mb-4">
              <BookOpen className="text-[#ff00cc]" size={18} />
              <h3 className="font-bold tracking-widest text-xs uppercase">Kernel Log</h3>
            </div>
            <div className="flex-1 overflow-y-auto font-mono text-[10px] space-y-1 pr-2">
              {logs.length === 0 && <p className="text-gray-600">Waiting for activity...</p>}
              {logs.map((log, i) => (
                <p key={i} className="text-cyan-100 flex gap-2">
                  <span className="text-[#ff00cc]">{`>`}</span>
                  {log}
                </p>
              ))}
            </div>
          </div>

          <div className="glass rounded-3xl p-6 animate-fade-in" style={{ animationDelay: '0.3s' }}>
             <h3 className="font-bold tracking-widest text-xs uppercase mb-4 opacity-50">Sovereignty Status</h3>
             <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Security Layer</span>
                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full border border-green-500/30">ENFORCED</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Data Integrity</span>
                  <span className="text-xs bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full border border-cyan-500/30">VERIFIED</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">M08 Retention</span>
                  <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full border border-purple-500/30">ROTATING</span>
                </div>
             </div>
          </div>
        </div>
      </div>
    </main>
  )
}
