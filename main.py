import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, validator

app = FastAPI(title="String Analyzer Service", version="1.0.0")

# In-memory storage (use a database in production)
string_storage: Dict[str, dict] = {}


# Request/Response Models
class StringInput(BaseModel):
    value: str

    @validator("value")
    def validate_value(cls, v):
        if not isinstance(v, str):
            raise ValueError("Value must be a string")
        return v


class StringProperties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]


class StringResponse(BaseModel):
    id: str
    value: str
    properties: StringProperties
    created_at: str


class StringListResponse(BaseModel):
    data: List[StringResponse]
    count: int
    filters_applied: Dict


class NaturalLanguageResponse(BaseModel):
    data: List[StringResponse]
    count: int
    interpreted_query: Dict


# Helper Functions
def compute_sha256(text: str) -> str:
    """Compute SHA-256 hash of the input string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_palindrome(text: str) -> bool:
    """Check if string is a palindrome (case-insensitive)."""
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


def count_unique_characters(text: str) -> int:
    """Count distinct characters in the string."""
    return len(set(text))


def count_words(text: str) -> int:
    """Count words separated by whitespace."""
    return len(text.split())


def character_frequency(text: str) -> Dict[str, int]:
    """Create character frequency map."""
    freq_map = {}
    for char in text:
        freq_map[char] = freq_map.get(char, 0) + 1
    return freq_map


def analyze_string(value: str) -> dict:
    """Analyze string and compute all properties."""
    sha256_hash = compute_sha256(value)

    properties = StringProperties(
        length=len(value),
        is_palindrome=is_palindrome(value),
        unique_characters=count_unique_characters(value),
        word_count=count_words(value),
        sha256_hash=sha256_hash,
        character_frequency_map=character_frequency(value),
    )

    return {
        "id": sha256_hash,
        "value": value,
        "properties": properties.dict(),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


def parse_natural_language_query(query: str) -> Dict:
    """Parse natural language query into filters."""
    query_lower = query.lower()
    filters = {}

    # Parse palindrome queries
    if "palindrom" in query_lower:
        filters["is_palindrome"] = True

    # Parse word count
    if "single word" in query_lower:
        filters["word_count"] = 1
    elif "two word" in query_lower or "2 word" in query_lower:
        filters["word_count"] = 2
    else:
        # Look for explicit word count
        word_count_match = re.search(r"(\d+)\s+word", query_lower)
        if word_count_match:
            filters["word_count"] = int(word_count_match.group(1))

    # Parse length constraints
    longer_match = re.search(r"longer than (\d+)", query_lower)
    if longer_match:
        filters["min_length"] = int(longer_match.group(1)) + 1

    shorter_match = re.search(r"shorter than (\d+)", query_lower)
    if shorter_match:
        filters["max_length"] = int(shorter_match.group(1)) - 1

    # Parse character containment
    contains_match = re.search(
        r"contain(?:ing|s)?\s+(?:the\s+)?(?:letter\s+)?([a-z])", query_lower
    )
    if contains_match:
        filters["contains_character"] = contains_match.group(1)

    # Handle "first vowel" as 'a'
    if "first vowel" in query_lower:
        filters["contains_character"] = "a"

    return filters


def apply_filters(data: List[dict], filters: Dict) -> List[dict]:
    """Apply filters to string data."""
    filtered_data = data

    for key, value in filters.items():
        if key == "is_palindrome":
            filtered_data = [
                item
                for item in filtered_data
                if item["properties"]["is_palindrome"] == value
            ]
        elif key == "min_length":
            filtered_data = [
                item for item in filtered_data if item["properties"]["length"] >= value
            ]
        elif key == "max_length":
            filtered_data = [
                item for item in filtered_data if item["properties"]["length"] <= value
            ]
        elif key == "word_count":
            filtered_data = [
                item
                for item in filtered_data
                if item["properties"]["word_count"] == value
            ]
        elif key == "contains_character":
            filtered_data = [item for item in filtered_data if value in item["value"]]

    return filtered_data


# API Endpoints


@app.post("/strings", status_code=201, response_model=StringResponse)
async def create_string(input_data: StringInput):
    """Create and analyze a new string."""
    try:
        # Check if string already exists
        sha256_hash = compute_sha256(input_data.value)
        if sha256_hash in string_storage:
            raise HTTPException(
                status_code=409, detail="String already exists in the system"
            )

        # Analyze and store the string
        analyzed_data = analyze_string(input_data.value)
        string_storage[sha256_hash] = analyzed_data

        return analyzed_data
    except ValueError as e:
        raise HTTPException(
            status_code=422, detail=f"Invalid data type for 'value': {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad request: {str(e)}")


@app.get("/strings/{string_value}", response_model=StringResponse)
async def get_string(string_value: str = Path(...)):
    """Get a specific string by its value."""
    sha256_hash = compute_sha256(string_value)

    if sha256_hash not in string_storage:
        raise HTTPException(
            status_code=404, detail="String does not exist in the system"
        )

    return string_storage[sha256_hash]


@app.get("/strings", response_model=StringListResponse)
async def get_all_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None, ge=0),
    max_length: Optional[int] = Query(None, ge=0),
    word_count: Optional[int] = Query(None, ge=0),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
):
    """Get all strings with optional filtering."""
    try:
        # Collect applied filters
        filters = {}
        if is_palindrome is not None:
            filters["is_palindrome"] = is_palindrome
        if min_length is not None:
            filters["min_length"] = min_length
        if max_length is not None:
            filters["max_length"] = max_length
        if word_count is not None:
            filters["word_count"] = word_count
        if contains_character is not None:
            filters["contains_character"] = contains_character

        # Get all strings
        all_strings = list(string_storage.values())

        # Apply filters
        filtered_strings = apply_filters(all_strings, filters)

        return {
            "data": filtered_strings,
            "count": len(filtered_strings),
            "filters_applied": filters,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid query parameter values or types: {str(e)}"
        )


@app.get("/strings/filter-by-natural-language", response_model=NaturalLanguageResponse)
async def filter_by_natural_language(query: str = Query(..., min_length=1)):
    """Filter strings using natural language queries."""
    try:
        # Parse natural language query
        filters = parse_natural_language_query(query)

        if not filters:
            raise HTTPException(
                status_code=400, detail="Unable to parse natural language query"
            )

        # Check for conflicting filters
        if "min_length" in filters and "max_length" in filters:
            if filters["min_length"] > filters["max_length"]:
                raise HTTPException(
                    status_code=422,
                    detail="Query parsed but resulted in conflicting filters",
                )

        # Get all strings and apply filters
        all_strings = list(string_storage.values())
        filtered_strings = apply_filters(all_strings, filters)

        return {
            "data": filtered_strings,
            "count": len(filtered_strings),
            "interpreted_query": {"original": query, "parsed_filters": filters},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Unable to parse natural language query: {str(e)}"
        )


@app.delete("/strings/{string_value}", status_code=204)
async def delete_string(string_value: str = Path(...)):
    """Delete a specific string."""
    sha256_hash = compute_sha256(string_value)

    if sha256_hash not in string_storage:
        raise HTTPException(
            status_code=404, detail="String does not exist in the system"
        )

    del string_storage[sha256_hash]
    return None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "String Analyzer Service",
        "version": "1.0.0",
        "endpoints": {
            "POST /strings": "Create and analyze a new string",
            "GET /strings/{string_value}": "Get a specific string",
            "GET /strings": "Get all strings with optional filters",
            "GET /strings/filter-by-natural-language": "Filter strings using natural language",
            "DELETE /strings/{string_value}": "Delete a specific string",
        },
    }
