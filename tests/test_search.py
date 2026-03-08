import pytest
from src.modules.search.chapter_selection import parse_chapter_selection

def test_parse_all():
    chapters = [{"number": "1"}, {"number": "2"}]
    result = parse_chapter_selection(chapters, "all")
    assert len(result) == 2

def test_parse_range():
    chapters = [{"number": "1"}, {"number": "2"}, {"number": "3"}]
    result = parse_chapter_selection(chapters, "1-2")
    assert len(result) == 2
    assert result[0]["number"] == "1"
    assert result[1]["number"] == "2"

def test_parse_individual():
    chapters = [{"number": "1"}, {"number": "2"}, {"number": "3"}]
    result = parse_chapter_selection(chapters, "1 3")
    assert len(result) == 2
    assert result[0]["number"] == "1"
    assert result[1]["number"] == "3"
