"""
For testing different reranker limits, this script generates Lorem Ipsum texts of varying lengths

Generate Lorem Ipsum texts at lengths of 100, 200, 300, 400, and 500, etc. up through 3000 words.
"""

import random
from mentor.curator.curate_client import query_server

LOREM_IPSUM_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut "
    "labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris "
    "nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit "
    "esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in "
    "culpa qui officia deserunt mollit anim id est laborum".split()
)


def generate_lorem_ipsum(word_count):
    """Generate Lorem Ipsum text with the specified word count."""
    return " ".join(random.choices(LOREM_IPSUM_WORDS, k=word_count))


texts = []
for length in range(50, 3100, 50):
    lorem_text = generate_lorem_ipsum(length)
    texts.append({"length": length, "text": lorem_text})

for text in texts:
    try:
        results = query_server(query_string=text["text"])
        print(f"Length: {text['length']} characters: Success")
    except Exception as e:
        print(f"Length: {text['length']} characters: Failed")
