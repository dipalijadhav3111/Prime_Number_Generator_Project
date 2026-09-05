"""
FastAPI Main Application
Features:
- REST API for Prime Number Generation & Benchmarking
- Interactive Swagger UI at /docs
- In-memory / File-backed SQLite Logging (Timestamp, Range, Time Elapsed, Algorithm Chosen, Primes Count)
- Embedded Web Dashboard UI
- Robust Error Handling and Resource Management
"""
import time
import math
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.algorithms import PrimeEngineFactory, SegmentedSieveStrategy
from app.models import (
    PrimeRangeRequest, PrimeRangeResponse,
    PrimeCheckRequest, PrimeCheckResponse,
    NthPrimeRequest, NthPrimeResponse,
    BenchmarkRequest, BenchmarkResponse
)
from app.database import log_execution, get_recent_logs

app = FastAPI(
    title="Prime Generator Engine & REST API",
    description="High-performance algorithmic prime number generation, primality verification, and benchmarking service.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the interactive Web UI Dashboard"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Prime Generator Engine API is Running! Visit <a href='/docs'>/docs</a></h1>"


@app.post("/api/primes/range", response_model=PrimeRangeResponse)
def generate_primes_range(req: PrimeRangeRequest):
    """
    Generate all prime numbers in the range [start, end] with selected algorithm strategy.
    Logs execution: timestamp, range, time elapsed, algorithm chosen, and number of primes returned.
    """
    if req.start > req.end:
        raise HTTPException(status_code=400, detail="Start range cannot be greater than end range.")
    if req.end - req.start > 2_000_000:
        raise HTTPException(status_code=400, detail="Range size cannot exceed 2,000,000 in a single request.")

    strategy = PrimeEngineFactory.get_strategy(req.algorithm)
    
    t0 = time.perf_counter()
    primes = strategy.generate_primes_in_range(req.start, req.end)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Record execution into database as required by Part 2
    log_execution(
        algorithm_chosen=strategy.name,
        time_elapsed_ms=elapsed_ms,
        primes_count=len(primes),
        range_start=req.start,
        range_end=req.end,
        request_type="range"
    )

    return PrimeRangeResponse(
        start=req.start,
        end=req.end,
        algorithm_used=strategy.name,
        count=len(primes),
        execution_time_ms=round(elapsed_ms, 3),
        primes=primes
    )


@app.post("/api/primes/check", response_model=PrimeCheckResponse)
def check_primality(req: PrimeCheckRequest):
    """Check if a single number is prime and log execution details."""
    strategy = PrimeEngineFactory.get_strategy(req.algorithm)
    
    t0 = time.perf_counter()
    result = strategy.is_prime(req.number)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    log_execution(
        algorithm_chosen=strategy.name,
        time_elapsed_ms=elapsed_ms,
        primes_count=1 if result else 0,
        range_start=req.number,
        range_end=req.number,
        request_type="check",
        details=f"Primality test for {req.number}: {'PRIME' if result else 'COMPOSITE'}"
    )

    return PrimeCheckResponse(
        number=req.number,
        is_prime=result,
        algorithm_used=strategy.name,
        execution_time_ms=round(elapsed_ms, 4)
    )


@app.post("/api/primes/nth", response_model=NthPrimeResponse)
def get_nth_prime(req: NthPrimeRequest):
    """Find the N-th prime number (e.g. 1st = 2, 2nd = 3, 100th = 541)."""
    t0 = time.perf_counter()
    
    if req.n == 1:
        ans = 2
    else:
        # Prime Number Theorem upper bound approximation
        # p_n < n * (ln(n) + ln(ln(n))) for n >= 6
        if req.n < 6:
            upper = 15
        else:
            fn = float(req.n)
            upper = int(fn * (math.log(fn) + math.log(math.log(fn))) * 1.15)
        
        sieve = SegmentedSieveStrategy()
        primes = sieve.generate_primes_in_range(2, upper)
        
        if len(primes) < req.n:
            primes = sieve.generate_primes_in_range(2, upper * 2)
            
        if len(primes) < req.n:
            raise HTTPException(status_code=500, detail="Could not compute Nth prime within upper limit bounds.")
        ans = primes[req.n - 1]

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    log_execution(
        algorithm_chosen="Segmented Sieve",
        time_elapsed_ms=elapsed_ms,
        primes_count=1,
        range_start=1,
        range_end=ans,
        request_type="nth",
        details=f"Found {req.n}-th prime = {ans}"
    )

    return NthPrimeResponse(
        n=req.n,
        nth_prime=ans,
        execution_time_ms=round(elapsed_ms, 3)
    )


@app.post("/api/benchmark", response_model=BenchmarkResponse)
def run_benchmark(req: BenchmarkRequest):
    """Benchmark all 4 algorithms on the given range to compare performance."""
    if req.start > req.end:
        raise HTTPException(status_code=400, detail="Start range cannot be greater than end range.")
    results = PrimeEngineFactory.benchmark_all(req.start, req.end)
    return BenchmarkResponse(
        start=req.start,
        end=req.end,
        results=results
    )


@app.get("/api/history")
def get_history(limit: int = Query(default=15, le=50)):
    """Retrieve recent prime calculation logs from the database."""
    logs = get_recent_logs(limit)
    return [
        {
            "id": l.id,
            "type": l.request_type,
            "range": f"[{l.range_start}, {l.range_end}]" if l.range_start is not None else "-",
            "algorithm": l.algorithm_chosen,
            "count": l.primes_count,
            "time_ms": l.time_elapsed_ms,
            "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "details": l.details
        }
        for l in logs
    ]
