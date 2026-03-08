import asyncio
import sys
import shutil
from pathlib import Path
from src.core.config import DOWNLOAD_DIR
from src.api.provider_registry import ProviderRegistry
from src.core.localization import STRINGS, get_string
from src.modules.search.search_manga import search_manga
from src.modules.search.get_chapters import get_manga_chapters
from src.modules.search.chapter_selection import parse_chapter_selection
from src.modules.download.download_chapter import download_chapter_images
from src.modules.pdf.pdf_generator import create_pdf_from_images
from src.ui.terminal import display_welcome, display_error, display_success, create_progress_bar, console

async def async_main():
    display_welcome()

    # 0. Language Selection
    import inquirer
    lang_choice = inquirer.list_input(
        "Selecione o idioma alvo (Target Language):",
        choices=[
            "Português (Brasil)",
            "English",
            "Español"
        ],
        carousel=True
    )

    lang_map = {
        "Português (Brasil)": "pt-br",
        "English": "en",
        "Español": "es"
    }
    lang = lang_map[lang_choice]
    texts = STRINGS[lang]

    provider = ProviderRegistry.get_provider("mangadex")
    try:
        # 1. Search
        manga_name = console.input(f"[bold cyan]{texts['manga_title_prompt']}[/bold cyan] ").strip()
        if not manga_name:
            display_error(texts["manga_title_empty_error"])
            return

        with console.status(f"[bold yellow]{texts['fetching_chapters']}[/bold yellow]"):
            manga_data = await search_manga(manga_name, provider)

        if not manga_data:
            display_error(texts["no_manga_found"].format(manga_name))
            return

        display_success(texts["manga_found"].format(manga_data['title']))

        # 2. Chapters (Intelligent Search: User Lang + English for IA)
        target_langs = [lang, "en"]
        with console.status(texts["fetching_chapters"]):
            chapters = await get_manga_chapters(manga_data["id"], target_langs, provider)

        if not chapters: # pragma: no cover
            display_error("Nenhum capítulo disponível nos idiomas selecionados.")
            return # pragma: no cover

        # Intelligent Grouping: Prioritize pt-br, fallback to en
        unique_chapters = {}
        for c in chapters:
            num = c["number"]
            # Prioritize target language or existing entry with better lang
            if num not in unique_chapters or c["lang"] == lang:
                unique_chapters[num] = c

        sorted_chaps = sorted(unique_chapters.values(), key=lambda x: float(x["number"]) if x["number"].replace('.', '', 1).isdigit() else 0)

        console.print(f"\n[bold]{texts['available_chapters']}[/bold]")
        for c in sorted_chaps[-15:]:
            lang_tag = f"[green]({c['lang']})[/green]" if c['lang'] == lang else f"[yellow]({c['lang']} - Traduzível)[/yellow]"
            console.print(f" • Capítulo {c['number']} {lang_tag}")

        selection = console.input(f"\n[bold cyan]{texts['chapters_range_prompt']}[/bold cyan] ").strip()
        to_download = parse_chapter_selection(sorted_chaps, selection)

        if not to_download: # pragma: no cover
            display_error("Nenhum capítulo selecionado.")
            return # pragma: no cover

        needs_translation = any(c["lang"] != lang for c in to_download)

        use_ai = False
        if needs_translation: # pragma: no cover
            console.print(f"\n[bold yellow]ℹ️ {texts['ai_prompt_translation'].format(lang)}[/bold yellow]")
            use_ai = console.input("> ").lower() == 's'
        elif console.input(f"\n[bold cyan]Deseja ativar OCR/Melhoria de imagem (Omni-Reader)? (s/n): [/bold cyan]").lower() == 's':
            use_ai = True

        ocr_engine = None
        translator = None

        if use_ai:
            from src.modules.ai.ocr_engine import OCREngine
            from src.modules.ai.translator import TranslationEngine
            with console.status(f"[bold magenta]{texts['ai_initializing']}[/bold magenta]"):
                # Detect most common source lang in selection for engine init
                # For simplified v5, we assume the first chapter needing translation defines the source
                first_foreign = next((c for c in to_download if c["lang"] != lang), to_download[0])
                source_lang = first_foreign["lang"].split('-')[0] # normalize to 2 chars (en, ja, es)
                target_lang = lang.split('-')[0]

                ocr_engine = OCREngine(languages=[source_lang])
                translator = TranslationEngine(from_code=source_lang, to_code=target_lang)

        with create_progress_bar() as progress:
            task = progress.add_task("[cyan]Processando capítulos...", total=len(to_download))

            for chap in to_download:
                progress.update(task, description=f"Baixando Cap. {chap['display']}")
                # manga_path is not defined here, assuming it should be defined earlier or passed.
                # For now, let's assume it's a global or defined above this snippet.
                # If not, this will cause an error. Assuming it's defined somewhere.
                # For the purpose of this edit, I'll keep it as is.
                manga_path = DOWNLOAD_DIR / manga_data['title'] # Assuming manga_path should be defined here
                manga_path.mkdir(parents=True, exist_ok=True)

                chap_dir = manga_path / f"Capitulo_{chap['display']}"
                chap_dir.mkdir(exist_ok=True)

                images = await download_chapter_images(chap["id"], chap_dir, provider)

                if images:
                    pdf_path = manga_path / f"Capitulo_{chap['display']}.pdf"
                    progress.update(task, description=f"Gerando PDF (IA: {'Ativa' if use_ai else 'Inativa'})")
                    create_pdf_from_images(images, pdf_path, ocr_engine, translator)
                    # Cleanup images
                    shutil.rmtree(chap_dir)

                progress.advance(task)

        display_success("\n[bold green]✨ Processo concluído com sucesso![/bold green]")

    finally:
        await provider.close()

if __name__ == "__main__":  # pragma: no cover
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt: # pragma: no cover
        console.print("\n[bold red]Interrompido pelo usuário. Saindo...[/bold red]")
        sys.exit(0)
    except Exception as e: # pragma: no cover
        display_error(f"Erro fatal: {e}")
        sys.exit(1)
