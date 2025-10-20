import hashlib

from models import StringProperties


def analyze_string(s: str) -> StringProperties:
    length = len(s)
    normalized_s = "".join(filter(str.isalnum, s)).lower()
    is_palindrome = normalized_s == normalized_s[::-1]
    unique_characters = len(set(s))
    word_count = len(s.split())
    sha256_hash = hashlib.sha256(s.encode("utf-8")).hexdigest()
    character_frequencies = {}

    for char in s:
        if char in character_frequencies:
            character_frequencies[char] += 1
        else:
            character_frequencies[char] = 1

    return StringProperties(
        length=length,
        is_palindrome=is_palindrome,
        unique_characters=unique_characters,
        word_count=word_count,
        sha256_hash=sha256_hash,
        character_frequencies=character_frequencies,
    )
