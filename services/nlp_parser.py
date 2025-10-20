from typing import Any, Dict


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """
    A mock function to parse natural language queries into structured filter criteria.
    In a real implementation, this would involve NLP techniques.
    """
    # This is a simplified example. A real implementation would be more complex.
    filters = {}
    query = query.lower()
    if "palindrome" in query or "palindromic" in query:
        filters["is_palindrome"] = True
    if "single word" in query or "one word" in query:
        filters["word_count"] = 1
    elif "two words" in query:
        filters["word_count"] = 2
    words = query.split()
    for i, word in enumerate(words):
        try:
            if word == "longer" and i < len(words) - 2 and words[i + 1] == "than":
                length_str = words[i + 2]
                filters["min_length"] = int(length_str)
            elif word == "shorter" and i < len(words) - 2 and words[i + 1] == "than":
                length_str = words[i + 2]
                filters["max_length"] = int(length_str)
        except ValueError:
            pass
    # --- Contains Character ---
    vowels = ["a", "e", "i", "o", "u"]
    for char in vowels:
        if "first vowel" in query and "contains" in query:
            filters["contains_character"] = "a"
            break

    if "containing the letter" in query:
        # Simple extraction of the last letter in the phrase
        # E.g., "strings containing the letter z"
        try:
            char = words[words.index("letter") + 1].strip()
            if len(char) == 1 and char.isalpha():
                filters["contains_character"] = char
        except (IndexError, ValueError):
            pass

    return filters
