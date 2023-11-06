"""Parsers service"""

import logging
import re
from typing import Dict, List

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_bible_verse(verse_str: str) -> List[int]:
    """
    Returns an array of numbers representing verses in the bible.
    ```python
    verses_idx = parse_bible_verse("1-3,5,8")
    #> [1,2,3,5,8]
    ```
    """
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


# 150:10-12,14-16,18,20,2:10-12,13-14,3:15


class GrammaticLexicalParser:
    """Lexical parser for the bible verse querying grammar"""

    def __init__(self):
        self.input_str = ""
        self.position = 0
        self.cursor = 0
        self.result = {}

    def parse(self, input_str: str):
        """Parse input str"""
        result = {}
        current_key = None
        current_values = []
        cursor = 0

        while cursor < len(input_str):
            char = input_str[cursor]

            if char.isdigit():
                num = ""
                while cursor < len(input_str) and input_str[cursor].isdigit():
                    num += input_str[cursor]
                    cursor += 1

                num = int(num)

                if current_key is not None:
                    current_values.append(num)
                else:
                    current_key = num

            elif char == ":":
                cursor += 1
                current_values = []
                result[current_key] = current_values

            elif char == " ":
                cursor += 1
                num = ""
                while cursor < len(input_str) and input_str[cursor].isdigit():
                    num += input_str[cursor]
                    cursor += 1

                num = int(num)

                current_key = num
                current_values = []

            elif char == "-":
                cursor += 1
                range_end = ""
                while cursor < len(input_str) and input_str[cursor].isdigit():
                    range_end += input_str[cursor]
                    cursor += 1

                range_end = int(range_end)
                current_values.extend(
                    range(current_values[-1] + 1, range_end + 1)
                )

            elif char == ",":
                cursor += 1
        self.result = result

    def get_result(self) -> Dict[int, List[int]]:
        """Get parser results"""
        return self.result
