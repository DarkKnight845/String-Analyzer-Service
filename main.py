from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse

from models import (
    FilterResponse,
    NaturalLanguageQueryResponse,
    StringAnalysisResult,
    StringValue,
)
from services.nlp_parser import parse_natural_language_query
from services.storage import storage_service

app = FastAPI(
    title="String Analyzer Service",
    description="A service to analyze strings and provide various properties.",
)


@app.post(
    "/strings",
    response_model=StringAnalysisResult,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze and store a new string",
)
async def create_string(string_value: StringValue):
    """
    Analyze the provided string and store its properties.
    """
    try:
        analysis_result = storage_service.create_string(string_value.value)
        return analysis_result
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="String already exists"
        )

    response_content = analysis_result.model_dump(by_alias=True)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response_content)


@app.get(
    "/strings/{string_id}",
    response_model=StringAnalysisResult,
    summary="Retrieve string analysis by ID",
)
async def get_string(string_id: str):
    """
    Retrieve the analysis result of a string by its unique identifier (SHA-256 hash).
    """
    analysis_result = storage_service.get_string_by_id(string_id)
    if not analysis_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="String not found"
        )
    return analysis_result


@app.get(
    "/strings",
    response_model=FilterResponse,
    summary="Retrieve all string analyses with optional filtering",
)
async def get_all_strings(
    is_palindrome: bool | None = Query(
        None, description="Filter by palindrome property"
    ),
    min_length: int | None = Query(None, description="Filter by minimum string length"),
    max_length: int | None = Query(None, description="Filter by maximum string length"),
    word_count: int | None = Query(None, description="Filter by exact word count"),
    contains_character: str | None = Query(
        None, description="Filter strings containing a specific character"
    ),
):
    """
    Retrieve all string analysis results, optionally applying filters.
    """
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

    if (min_length is not None and max_length is not None) and (
        min_length > max_length
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_length cannot be greater than max_length",
        )

    results = storage_service.get_all_strings(filters)
    response = FilterResponse(
        data=results,
        count=len(results),
        interpreted_query=filters,
    )
    return response


@app.get(
    "/strings/nlp-query",
    response_model=NaturalLanguageQueryResponse,
    summary="Retrieve string analyses based on a natural language query",
)
async def nlp_query_strings(
    query: str = Query(..., description="Natural language query for filtering strings"),
):
    """
    Retrieve string analysis results based on a natural language query.
    """
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter is required",
        )
    filters = parse_natural_language_query(query)
    if not filters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not interpret the natural language query",
        )
    results = storage_service.get_all_strings(filters)
    response = NaturalLanguageQueryResponse(
        data=results,
        count=len(results),
        interpreted_query=filters,
    )
    return response


@app.delete(
    "/strings/{string_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete string analysis by ID",
)
async def delete_string(string_id: str):
    """
    Delete the analysis result of a string by its unique identifier (SHA-256 hash).
    """
    success = storage_service.delete_string_by_id(string_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="String not found"
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
