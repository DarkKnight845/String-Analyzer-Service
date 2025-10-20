from datetime import datetime
from typing import Any, Dict, List, Optional

from models import StringAnalysisResult
from utils.analyzer import analyze_string

STORE = {}


class StorageService:
    """
    Service for storing and retrieving string analysis results.
    """

    def create_string(self, value: str) -> StringAnalysisResult:
        """
        Analyze the string and store its properties."""
        properties = analyze_string(value)
        string_id = properties.sha256_hash
        if string_id in STORE:
            raise ValueError("String already exists")
        analysis_result = StringAnalysisResult(
            id=string_id, properties=properties, created_at=datetime.utcnow()
        )
        STORE[string_id] = analysis_result
        return analysis_result

    def get_string_by_id(self, string_id: str) -> Optional[StringAnalysisResult]:
        """
        Retrieve a string analysis result by its unique identifier (SHA-256 hash).
        """
        return STORE.get(string_id)

    def delete_string_by_id(self, string_id: str) -> bool:
        """
        Delete a string analysis result by its unique identifier (SHA-256 hash).
        """
        if string_id in STORE:
            del STORE[string_id]
            return True
        return False

    def get_all_strings(self, filters: Dict[str, Any]) -> List[StringAnalysisResult]:
        """
        Retrieve all string analysis results, optionally applying filters.
        """
        results: list[StringAnalysisResult] = []

        for analysis in STORE.values():
            props = analysis.properties
            match = True

            # palindrome filter
            if (
                "is_palindrome" in filters
                and props.is_palindrome != filters["is_palindrome"]
            ):
                match = False

            # min_length filter
            if "min_length" in filters and props.length < filters["min_length"]:
                match = False

            # max_length filter
            if "max_length" in filters and props.length > filters["max_length"]:
                match = False

            # word_count filter
            if "word_count" in filters and props.word_count != filters["word_count"]:
                match = False

            # case sensitive match in original string
            if "contains" in filters:
                contains_value = filters["contains"]
                if contains_value not in analysis.properties.character_frequencies:
                    match = False

            if match:
                results.append(analysis)
        return results


storage_service = StorageService()
