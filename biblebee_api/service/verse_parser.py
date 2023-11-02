"""Parsers service"""
from typing import List
import re


def parse_bible_verse(verse_str) -> List[int]:
    """Returns an array of numbers representing verses in the bible"""
    # Define a regular expression pattern to match verse ranges
    verse_pattern = r"(\d+)(?:-(\d+))?"

    # Use re.findall to extract matched verse numbers
    verse_numbers = []
    for match in re.finditer(verse_pattern, verse_str):
        start, end = match.groups()
        if end is None:
            verse_numbers.append(int(start))
        else:
            verse_numbers.extend(range(int(start), int(end) + 1))

    return verse_numbers
