'use client'

import { Search } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

interface Manga {
  id: string
  title: string
  cover: string
  provider: string
}

interface MangaGridProps {
  mangas: Manga[]
  onSelect: (manga: Manga) => void
  loading: boolean
}

export default function MangaGrid({ mangas, onSelect, loading }: MangaGridProps) {
  const { t } = useLanguage()

  if (loading && mangas.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-[#00f2ff] rounded-full animate-spin shadow-[0_0_15px_rgba(0,242,255,0.2)]"></div>
        <p className="text-gray-500 text-xs font-bold uppercase tracking-widest animate-pulse">Acessando Dados...</p>
      </div>
    )
  }

  if (mangas.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-gray-500 gap-4 glass rounded-3xl animate-fade-in">
        <div className="w-16 h-16 rounded-full bg-gray-900/50 flex items-center justify-center border border-white/5">
          <Search size={32} className="text-gray-700" />
        </div>
        <p className="text-lg font-medium tracking-wide">{t('waiting_search')}</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 animate-fade-in">
      {mangas.map((manga, i) => (
        <div 
          key={manga.id} 
          className="group glass cursor-pointer hover:glass-active transition-all p-3 rounded-2xl flex flex-col gap-3 animate-slide-up"
          style={{ animationDelay: `${i * 0.03}s` }}
          onClick={() => onSelect(manga)}
        >
          <div className="aspect-[3/4] rounded-xl overflow-hidden relative shadow-2xl">
            <img 
              src={`http://localhost:8000/api/v1/manga/proxy/cover?url=${encodeURIComponent(manga.cover || '')}`} 
              alt={manga.title} 
              className="object-cover w-full h-full group-hover:scale-110 transition-transform duration-700 ease-out"
              loading="lazy"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-60 group-hover:opacity-40 transition-opacity"></div>
            <div className="absolute bottom-3 left-3 right-3">
              <p className="font-bold text-xs line-clamp-2 leading-snug text-white group-hover:text-[#00f2ff] transition-colors">{manga.title}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
