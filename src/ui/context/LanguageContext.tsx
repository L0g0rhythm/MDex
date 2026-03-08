'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'

type Language = 'pt' | 'en' | 'es'

interface Translations {
  [key: string]: {
    [key in Language]: string
  }
}

const translations: Translations = {
  search_placeholder: {
    pt: 'Pesquisar mangá...',
    en: 'Search manga...',
    es: 'Buscar manga...'
  },
  search_btn: {
    pt: 'BUSCAR',
    en: 'SEARCH',
    es: 'BUSCAR'
  },
  back_btn: {
    pt: 'Voltar para resultados',
    en: 'Back to results',
    es: 'Volver a resultados'
  },
  download_btn: {
    pt: 'BAIXAR',
    en: 'DOWNLOAD',
    es: 'DESCARGAR'
  },
  selected_count: {
    pt: 'selecionados',
    en: 'selected',
    es: 'seleccionados'
  },
  chapter: {
    pt: 'Capítulo',
    en: 'Chapter',
    es: 'Capítulo'
  },
  no_title: {
    pt: 'Sem Título',
    en: 'No Title',
    es: 'Sin Título'
  },
  waiting_search: {
    pt: 'Qual mangá vamos ler hoje?',
    en: 'Which manga are we reading today?',
    es: '¿Qué manga vamos a leer hoy?'
  },
  downloading: {
    pt: 'Baixando...',
    en: 'Downloading...',
    es: 'Descargando...'
  },
  completed: {
    pt: 'Concluído',
    en: 'Completed',
    es: 'Completado'
  },
  cancel: {
    pt: 'Cancelar',
    en: 'Cancel',
    es: 'Cancelar'
  },
  use_ai_mode: {
    pt: 'Traduzir com IA',
    en: 'Translate with AI',
    es: 'Traducir con IA'
  },
  settings: {
    pt: 'Configurações',
    en: 'Settings',
    es: 'Configuración'
  },
  about: {
    pt: 'Sobre o MDex',
    en: 'About MDex',
    es: 'Sobre MDex'
  },
  download_path: {
    pt: 'Caminho de Download',
    en: 'Download Path',
    es: 'Ruta de Descarga'
  },
  save: {
    pt: 'Salvar',
    en: 'Save',
    es: 'Guardar'
  },
  version: {
    pt: 'Versão',
    en: 'Version',
    es: 'Versión'
  },
  creator: {
    pt: 'Criador',
    en: 'Creator',
    es: 'Creador'
  }
}

interface LanguageContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: (key: string) => string
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>('pt')

  const t = (key: string) => {
    return translations[key]?.[language] || key
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}
