'use client'

import { X, Settings, Info, FolderOpen, Github, ExternalLink, Save, CheckCircle2, Search } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'
import { useState, useEffect } from 'react'

interface SettingsModalProps {
  onClose: () => void
}

export default function SettingsModal({ onClose }: SettingsModalProps) {
  const { t } = useLanguage()
  const [downloadPath, setDownloadPath] = useState('')
  const [about, setAbout] = useState<any>(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/settings')
      .then(r => r.json())
      .then(data => {
        setDownloadPath(data.download_dir || '')
      })
    
    fetch('http://localhost:8000/api/v1/about')
      .then(r => r.json())
      .then(data => {
        console.log("About Data:", data)
        setAbout(data)
      })
      .catch(err => console.error("About fetch failed:", err))
  }, [])

  const openExplorer = async () => {
    try {
      const resp = await fetch('http://localhost:8000/api/v1/system/select-folder')
      const data = await resp.json()
      if (data.path) setDownloadPath(data.path)
    } catch (e) {
      console.error("Explorer failed", e)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await fetch('http://localhost:8000/api/v1/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ download_dir: downloadPath })
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-fade-in">
      <div className="bg-[#0f172a] border border-white/10 w-full max-w-2xl rounded-[32px] overflow-hidden flex flex-col shadow-2xl">
        <div className="p-6 border-b border-white/5 flex items-center justify-between bg-black/20">
          <div className="flex items-center gap-3">
            <Settings className="text-[#00f2ff] w-6 h-6" />
            <h1 className="text-xl font-bold text-white">{t('settings')}</h1>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
            <X className="text-slate-400" />
          </button>
        </div>

        <div className="p-8 space-y-8 overflow-y-auto">
          {/* Download Path Section */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-cyan-400">
              <FolderOpen size={18} />
              <h2 className="text-sm font-bold uppercase tracking-widest">{t('download_path')}</h2>
            </div>
            <div className="flex gap-2">
              <input 
                type="text" 
                value={downloadPath}
                onChange={(e) => setDownloadPath(e.target.value)}
                className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-[#00f2ff] transition-all"
                placeholder="Ex: C:\Downloads\MDex"
              />
              <button 
                onClick={openExplorer}
                className="p-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-cyan-400 transition-all"
                title="Abrir Explorador"
              >
                <Search size={20} />
              </button>
              <button 
                onClick={handleSave}
                disabled={saving}
                className={`px-6 rounded-xl font-bold text-xs flex items-center gap-2 transition-all ${
                  saved ? 'bg-emerald-500 text-white' : 'bg-[#00f2ff] text-black hover:scale-105'
                }`}
              >
                {saved ? <CheckCircle2 size={16} /> : <Save size={16} />}
                {saved ? 'OK' : t('save')}
              </button>
            </div>
          </section>

          {/* About Section */}
          <section className="space-y-4 pt-4 border-t border-white/5">
            <div className="flex items-center gap-2 text-slate-400">
              <Info size={18} />
              <h2 className="text-sm font-bold uppercase tracking-widest">{t('about')}</h2>
            </div>
            
            <div className="bg-white/5 border border-white/5 rounded-2xl overflow-hidden divide-y divide-white/5">
              <div className="grid grid-cols-2 p-4 items-center gap-4">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">{t('version')}</span>
                <span className="text-sm text-cyan-400 font-mono font-bold text-right">{about?.version || 'v3.8.4'}</span>
              </div>
              <div className="grid grid-cols-2 p-4 items-center gap-4">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">{t('creator')}</span>
                <span className="text-sm text-[#ff00cc] font-black uppercase tracking-tighter text-right">{about?.creator || 'L0g0rhythm'}</span>
              </div>
              <div className="grid grid-cols-2 p-4 items-center gap-4">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Website</span>
                <a 
                  href={about?.site || 'https://l0g0rhythm.com.br'} 
                  target="_blank" 
                  rel="noreferrer"
                  className="text-sm text-cyan-400 font-bold flex items-center justify-end gap-2 hover:text-[#00f2ff] transition-all group"
                >
                  l0g0rhythm.com.br
                  <ExternalLink size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </a>
              </div>
              <div className="grid grid-cols-2 p-4 items-center gap-4">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Repository</span>
                <a 
                  href={about?.repo || 'https://github.com/L0g0rhythm/MDex'} 
                  target="_blank" 
                  rel="noreferrer"
                  className="text-sm text-cyan-400 font-bold flex items-center justify-end gap-2 hover:text-[#00f2ff] transition-all group"
                >
                  Github
                  <Github size={14} className="group-hover:scale-110 transition-transform" />
                  <ExternalLink size={12} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </a>
              </div>
            </div>
          </section>
        </div>

        <div className="p-6 bg-black/40 text-center">
            <p className="text-[10px] text-slate-600 font-mono uppercase tracking-[0.3em]">
                L0g0rhythm Authority Core
            </p>
        </div>
      </div>
    </div>
  )
}
