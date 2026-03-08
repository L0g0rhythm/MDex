'use client'

import { useState, useEffect, useRef } from 'react'
import { AlertCircle, CheckCircle2 } from 'lucide-react'
import Header from '../components/Header'
import MangaGrid from '../components/MangaGrid'
import ChapterModal from '../components/ChapterModal'
import SettingsModal from '../components/SettingsModal'
import { useLanguage } from '../context/LanguageContext'

export default function Home() {
  const { language, t } = useLanguage()
  const [query, setQuery] = useState('')
  const [mangas, setMangas] = useState<any[]>([])
  const [selectedManga, setSelectedManga] = useState<any>(null)
  const [chapters, setChapters] = useState<any[]>([])
  const [selectedChapterIds, setSelectedChapterIds] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState<{ [key: string]: number }>({})
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const [useAI, setUseAI] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    (window as any).toggleSettings = () => setShowSettings(true)
    connectWS()
    return () => {
        ws.current?.close()
        delete (window as any).toggleSettings
    }
  }, [])

  const connectWS = () => {
    const socket = new WebSocket('ws://localhost:8000/api/v1/ws/progress')
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'progress') {
        setProgress(prev => ({ ...prev, [data.chapter_id]: data.percentage }))
      }
    }
    socket.onclose = () => setTimeout(connectWS, 3000)
    ws.current = socket
  }

  const searchManga = async () => {
    if (!query) return
    setLoading(true)
    setError(null)
    setSuccess(null)
    setMangas([])
    setSelectedManga(null)
    setChapters([])
    setSelectedChapterIds([]) 
    
    try {
      const resp = await fetch(`http://localhost:8000/api/v1/manga/search?title=${encodeURIComponent(query)}`)
      if (!resp.ok) throw new Error('Kernel Offline ou Erro de Rede')
      const data = await resp.json()
      setMangas(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchChapters = async (manga: any) => {
    setSelectedManga(manga)
    setSelectedChapterIds([])
    setProgress({})
    setChapters([])
    try {
      const resp = await fetch(`http://localhost:8000/api/v1/manga/${manga.id}/chapters?lang=${language}`)
      const data = await resp.json()
      setChapters(data)
    } catch (err: any) {
      setError(err.message)
    }
  }

  const startDownload = async (combine: boolean = false, titles: string[] = []) => {
    if (!selectedManga || selectedChapterIds.length === 0) return
    setError(null)
    setSuccess(null)
    try {
      const response = await fetch('http://localhost:8000/api/v1/download/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          manga_id: selectedManga.id,
          manga_title: selectedManga.title,
          chapter_ids: selectedChapterIds,
          chapter_titles: titles,
          use_ai: useAI,
          combine_pdf: combine,
          target_lang: language === 'pt' ? 'pt-br' : language
        })
      })
      const data = await response.json()
      setSuccess(data.message)
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <main className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto flex flex-col">
      <Header 
        query={query} 
        setQuery={setQuery} 
        onSearch={searchManga} 
        loading={loading} 
      />

      {/* Notifications */}
      <div className="mb-8 space-y-4">
        {error && (
          <div className="glass border-l-4 border-red-500 p-4 flex items-center gap-3 animate-slide-up bg-red-500/5">
            <AlertCircle className="text-red-500" />
            <span className="text-red-200 text-sm font-medium">{error}</span>
          </div>
        )}
        {success && (
          <div className="glass border-l-4 border-[#00f2ff] p-4 flex items-center gap-3 animate-slide-up bg-cyan-500/5">
            <CheckCircle2 className="text-[#00f2ff]" />
            <span className="text-cyan-100 text-sm font-medium">{success}</span>
          </div>
        )}
      </div>

      <MangaGrid 
        mangas={mangas} 
        onSelect={fetchChapters} 
        loading={loading} 
      />

      {selectedManga && (
        <ChapterModal 
          manga={selectedManga}
          chapters={chapters}
          selectedIds={selectedChapterIds}
          setSelectedIds={setSelectedChapterIds}
          onClose={() => setSelectedManga(null)}
          onDownload={startDownload}
          progress={progress}
          setProgress={setProgress}
          useAI={useAI}
          setUseAI={setUseAI}
        />
      )}

      {showSettings && (
        <SettingsModal onClose={() => setShowSettings(false)} />
      )}
    </main>
  )
}
