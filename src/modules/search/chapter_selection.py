def parse_chapter_selection(chapters: list, choice: str):
    """
    Parses user input for chapter selection.
    Supports: 'all', 'todos', single numbers ('1', '5.5'), and ranges ('10-20').
    """
    if choice.lower() in ('all', 'todos'):
        return chapters
    
    if choice.lower() == 'last' and chapters:
        return [max(chapters, key=lambda x: float(x['number']) if x['number'] else 0)]

    selected = []
    parts = choice.split()

    chapter_map = {str(c['number']): c for c in chapters if c['number'] is not None}

    for part in parts:
        if '-' in part:
            try:
                start_s, end_s = part.split('-')
                start, end = float(start_s), float(end_s)
                for c in chapters:
                    if c['number'] is not None and start <= float(c['number']) <= end:
                        if c not in selected:
                            selected.append(c)
            except ValueError:  # pragma: no cover
                continue  # pragma: no cover
        elif part in chapter_map:
            if chapter_map[part] not in selected:
                selected.append(chapter_map[part])

    return sorted(selected, key=lambda x: float(x['number']) if x['number'] else 0)
