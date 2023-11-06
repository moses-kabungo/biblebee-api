"""the testing module for the bible verses parser."""

import logging
import pytest

from biblebee_api.service import verse_parser

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


test_cases = [
    {
        "input": "150:10-12,14,16-18,20 2:10,12-17,19 3:15",
        "expected": {
            150: [10, 11, 12, 14, 16, 17, 18, 20],
            2: [10, 12, 13, 14, 15, 16, 17, 19],
            3: [15],
        },
    }
]


@pytest.mark.parametrize("test_case", test_cases)
def test_parse_bible_verses(test_case):
    """test parsing of bible verses"""
    parser = verse_parser.GrammaticLexicalParser()
    parser.parse(test_case["input"])
    result = parser.get_result()
    print(f"results={result}")
    assert result[150] == test_case["expected"][150]
    assert result[2] == test_case["expected"][2]
    assert result[3] == test_case["expected"][3]
