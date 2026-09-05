"""Pydantic Schemas for Prime Generator API"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class PrimeRangeRequest(BaseModel):
    start: int = Field(default=1, ge=0, description="Start of range (inclusive)")
    end: int = Field(default=100, ge=1, le=10_000_000, description="End of range (inclusive, max 10M)")
    algorithm: Optional[str] = Field(default="segmented", description="Algorithm: 'segmented', 'sieve', 'trial', 'miller_rabin'")


class PrimeRangeResponse(BaseModel):
    start: int
    end: int
    algorithm_used: str
    count: int
    execution_time_ms: float
    primes: List[int]


class PrimeCheckRequest(BaseModel):
    number: int = Field(..., ge=0, description="Number to test for primality")
    algorithm: Optional[str] = Field(default="trial", description="Algorithm: 'trial', 'miller_rabin'")


class PrimeCheckResponse(BaseModel):
    number: int
    is_prime: bool
    algorithm_used: str
    execution_time_ms: float


class NthPrimeRequest(BaseModel):
    n: int = Field(..., ge=1, le=1_000_000, description="Nth prime to find (e.g. 100th prime)")


class NthPrimeResponse(BaseModel):
    n: int
    nth_prime: int
    execution_time_ms: float


class BenchmarkRequest(BaseModel):
    start: int = Field(default=1, ge=0)
    end: int = Field(default=100_000, ge=1, le=1_000_000)


class BenchmarkResponse(BaseModel):
    start: int
    end: int
    results: List[Dict[str, Any]]
