'use client'

import { Search, LayoutGrid, Loader2, Globe, Settings } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

interface HeaderProps {
  query: string
  setQuery: (q: string) => void
  onSearch: () => void
  loading: boolean
}

export default function Header({ query, setQuery, onSearch, loading }: HeaderProps) {
  const { language, setLanguage, t } = useLanguage()

  return (
    <header className="flex flex-col md:flex-row items-center justify-between gap-6 animate-fade-in mb-8">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 glass rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.2)]">
          <LayoutGrid className="text-[#00f2ff] w-6 h-6" />
        </div>
        <div>
            <h1 className="text-4xl font-black tracking-tighter neon-cyan">MDEX <span className="text-[#ff00cc]">SINGULARITY</span></h1>
        </div>
      </div>
      
      <div className="flex flex-col md:flex-row items-center gap-4 w-full md:w-auto">
        <button 
           onClick={() => (window as any).toggleSettings?.()}
           className="w-10 h-10 glass rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-all text-slate-400 hover:text-[#00f2ff] border border-white/5 order-3 md:order-1"
           title={t('settings')}
        >
            <Settings size={20} />
        </button>

        {/* Language Selector */}
        <div className="flex bg-gray-900/50 rounded-full p-1 border border-white/5 order-2 md:order-1">
          {(['pt', 'en', 'es'] as const).map((lang) => (
            <button
              key={lang}
              onClick={() => setLanguage(lang)}
              className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase transition-all ${
        language === lang ? 'bg-[#00f2ff] text-black' : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {lang}
            </button>
          ))}
        </div>

        <div className="relative w-full md:w-96 group order-1 md:order-2">
          <input 
            type="text" 
            placeholder={t('search_placeholder')}
            className="w-full h-12 pl-12 pr-4 glass rounded-full focus:outline-none focus:ring-2 focus:ring-[#00f2ff] transition-all text-sm"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearch()}
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-[#00f2ff] transition-colors" size={20} />
          <button 
            onClick={onSearch}
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-[#00f2ff] text-black px-4 py-1.5 rounded-full font-bold text-xs hover:scale-105 active:scale-95 transition-all"
          >
            {loading ? <Loader2 className="animate-spin" size={16} /> : t('search_btn')}
          </button>
        </div>
      </div>
    </header>
  )
}
