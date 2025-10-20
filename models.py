from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class StringProperties(BaseModel):
    length: int = Field(..., description="number of characters in the string")
    is_palindrome: bool = Field(
        ..., description="indicates if the string is a palindrome"
    )
    unique_characters: int = Field(
        ..., description="count of unique characters in the string"
    )
    word_count: int = Field(..., description="number of words in the string")
    sha256_hash: str = Field(..., description="SHA-256 hash of the string")
    character_frequencies: Dict[str, int] = Field(
        ..., description="frequency of each character in the string"
    )


class StringAnalysisResult(BaseModel):
    id: str = Field(
        ...,
        alias="sha256_hash_value",
        description="unique identifier for the analysis result, the original string's SHA-256 hash",
    )
    properties: StringProperties = Field(
        ..., description="detailed properties of the analyzed string"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="timestamp when the analysis was created",
    )


class StringValue(BaseModel):
    value: str = Field(
        ..., min_length=1, description="the original string value to be analyzed"
    )


class FilterResponse(BaseModel):
    data: List[StringAnalysisResult] = Field(
        ..., description="list of string analysis results matching the filter criteria"
    )
    count: int = Field(
        ...,
        description="total number of string analysis results matching the filter criteria",
    )
    interpreted_query: Dict[str, Any] = Field(
        ..., description="structured representation of the filter query used"
    )


class NaturalLanguageQueryResponse(BaseModel):
    data: List[StringAnalysisResult] = Field(
        ...,
        description="list of string analysis results matching the natural language query",
    )
    count: int
    interpreted_query: Dict[str, Any] = Field(
        ..., description="structured representation of the natural language query"
    )
