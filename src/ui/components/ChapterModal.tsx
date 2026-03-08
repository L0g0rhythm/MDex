'use client'

import { X, Download, Trash2, CheckCircle2, Loader2, StopCircle } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'
import { useState } from 'react'

interface ChapterModalProps {
  manga: any
  chapters: any[]
  selectedIds: string[]
  setSelectedIds: (ids: string[]) => void
  onClose: () => void
  onDownload: (combine: boolean, titles: string[]) => void
  progress: { [key: string]: number }
  setProgress: (val: { [key: string]: number }) => void
  useAI: boolean
  setUseAI: (val: boolean) => void
}

export default function ChapterModal({ 
  manga, 
  chapters, 
  selectedIds, 
  setSelectedIds, 
  onClose, 
  onDownload,
  progress,
  setProgress,
  useAI,
  setUseAI
}: ChapterModalProps) {
  const { t } = useLanguage()
  const [isCancelling, setIsCancelling] = useState(false)
  const [combinePDF, setCombinePDF] = useState(false)

  const toggleSelect = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id))
    } else {
      setSelectedIds([...selectedIds, id])
    }
  }

  const handleClear = () => {
    const newProgress = { ...progress }
    selectedIds.forEach(id => delete newProgress[id])
    setProgress(newProgress)
    setSelectedIds([])
  }

  const handleCancel = async () => {
    setIsCancelling(true)
    try {
      await fetch(`http://localhost:8000/api/v1/download/cancel?manga_id=${manga.id}`, { method: 'POST' })
    } catch (e) {
      console.error("Cancel failed", e)
    } finally {
      setIsCancelling(false)
    }
  }

  const isDownloading = Object.keys(progress).length > 0 && !Object.values(progress).every(v => v === 100)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-fade-in">
      <div className="bg-[#0f172a] border border-white/10 w-full max-w-4xl max-h-[90vh] rounded-[32px] overflow-hidden flex flex-col md:flex-row shadow-2xl">
        
        {/* Manga Preview Sidebar */}
        <div className="md:w-72 p-6 bg-black/20 border-r border-white/5 space-y-6 hidden md:block flex-shrink-0">
          <img 
            src={`http://localhost:8000/api/v1/manga/proxy/cover?url=${encodeURIComponent(manga.cover || '')}`} 
            className="w-full aspect-[3/4] object-cover rounded-2xl shadow-2xl border border-white/5" 
            alt={manga.title} 
          />
          
          <div className="space-y-4 pt-4 border-t border-white/5">
            <label className="flex items-center gap-3 cursor-pointer group">
              <div 
                onClick={() => setUseAI(!useAI)}
                className={`w-12 h-6 rounded-full transition-all relative ${useAI ? 'bg-[#00f2ff]' : 'bg-white/10'}`}
              >
                <div className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-all ${useAI ? 'translate-x-6' : ''}`} />
              </div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest group-hover:text-white transition-colors">
                {t('use_ai_mode')}
              </span>
            </label>

            <div className="pt-2">
                <label className="flex items-center gap-3 cursor-pointer group">
                    <div 
                        onClick={() => setCombinePDF(!combinePDF)}
                        className={`w-12 h-6 rounded-full transition-all relative ${combinePDF ? 'bg-cyan-500' : 'bg-white/10'}`}
                    >
                        <div className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-all ${combinePDF ? 'translate-x-6' : ''}`} />
                    </div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest group-hover:text-white transition-colors">
                        Consolidar PDF
                    </span>
                </label>
                <p className="text-[9px] text-slate-500 mt-2 leading-tight">
                    Une todos os capítulos selecionados em um único arquivo premium.
                </p>
            </div>
          </div>
        </div>

        {/* Chapter List Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="p-6 border-b border-white/5 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white truncate max-w-xs">{manga.title}</h2>
              <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest font-bold">
                {chapters.length} {t('chapters')}
              </p>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
              <X className="text-slate-400" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-2 custom-scrollbar">
            {chapters.map((chap) => {
              const chapProgress = progress[chap.id]
              const isSelected = selectedIds.includes(chap.id)
              const isExternal = chap.pages === 0 || !!chap.external_url
              const status = chapProgress === 100 ? 'done' : chapProgress > 0 ? 'loading' : isSelected ? 'queued' : isExternal ? 'external' : 'idle'

              return (
                <div 
                  key={chap.id}
                  onClick={() => !isExternal && toggleSelect(chap.id)}
                  className={`group p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between
                    ${status === 'done' ? 'bg-emerald-500/10 border-emerald-500/30' : 
                      status === 'loading' ? 'bg-cyan-500/10 border-cyan-500/30' :
                      status === 'external' ? 'bg-amber-500/5 border-amber-500/20 opacity-60 cursor-not-allowed' :
                      isSelected ? 'bg-white/5 border-[#00f2ff]/50' : 'bg-white/5 border-transparent hover:border-white/10'}
                  `}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 flex items-center justify-center font-mono text-xs font-bold rounded-xl border
                      ${status === 'external' ? 'bg-amber-500/10 border-amber-500/20 text-amber-500' : 'bg-white/5 border-white/5 text-white'}
                    `}>
                      {chap.chapter || '??'}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-white">{chap.title || t('no_title')}</p>
                        {status === 'external' && (
                          <span className="text-[8px] bg-amber-500/20 text-amber-500 px-1.5 py-0.5 rounded-full font-bold uppercase tracking-widest border border-amber-500/20">
                            Externo
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">
                        {chap.lang} {chap.pages > 0 && `• ${chap.pages} ${t('pages')}`}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {status === 'loading' && (
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-1.5 bg-black/40 rounded-full overflow-hidden">
                          <div className="h-full bg-cyan-500 transition-all duration-300" style={{ width: `${chapProgress}%` }} />
                        </div>
                        <span className="text-[10px] font-mono font-bold text-cyan-400">{chapProgress}%</span>
                      </div>
                    )}
                    {status === 'done' && <CheckCircle2 className="text-emerald-500 w-5 h-5" />}
                    {status === 'loading' && <Loader2 className="text-cyan-500 w-5 h-5 animate-spin" />}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="p-6 border-t border-white/5 bg-black/20 flex gap-4">
            {isDownloading ? (
               <button 
                onClick={handleCancel}
                disabled={isCancelling}
                className="flex-1 py-4 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all border border-red-500/20"
               >
                 {isCancelling ? <Loader2 className="animate-spin" /> : <StopCircle className="w-5 h-5" />}
                 {t('cancel')}
               </button>
            ) : (
              <button 
                onClick={() => {
                  const selectedChapters = chapters.filter(c => selectedIds.includes(c.id))
                  const titles = selectedChapters.map(c => `Cap ${c.chapter} - ${c.title || t('no_title')}`)
                  onDownload(combinePDF, titles)
                }}
                disabled={selectedIds.length === 0}
                className="flex-1 py-4 bg-[#00f2ff] hover:bg-[#00d8e6] text-black rounded-2xl font-bold flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(0,242,255,0.3)] disabled:opacity-50 disabled:shadow-none"
              >
                <Download className="w-5 h-5" />
                {t('download_btn')} {selectedIds.length > 0 && ` (${selectedIds.length})`}
              </button>
            )}
            <button 
              onClick={handleClear} 
              className="p-4 bg-white/5 hover:bg-red-500/10 text-slate-400 hover:text-red-500 rounded-2xl transition-all border border-white/5 hover:border-red-500/30"
              title="Limpar Seleção e Progresso"
            >
              <Trash2 className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
