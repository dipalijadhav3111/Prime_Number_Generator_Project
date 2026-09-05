"""
Prime Number Generation Algorithms & Strategy Pattern Implementation
Includes:
- Trial Division (Standard & Optimized 6k +/- 1)
- Classic Sieve of Eratosthenes
- Segmented Sieve of Eratosthenes (Memory-efficient for large bounds)
- Miller-Rabin Primality Test (Deterministic for 64-bit)
"""
import math
import time
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any


class PrimeAlgorithmStrategy(ABC):
    """Abstract Strategy interface for prime generation algorithms"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def generate_primes_in_range(self, start: int, end: int) -> List[int]:
        """Generate all primes between start and end (inclusive)"""
        pass

    @abstractmethod
    def is_prime(self, n: int) -> bool:
        """Check if a single number n is prime"""
        pass


class TrialDivisionStrategy(PrimeAlgorithmStrategy):
    """
    Trial Division Algorithm with 6k +/- 1 optimization.
    Time Complexity: O(sqrt(N)) for single test, O((R-L)*sqrt(R)) for range.
    Space Complexity: O(1) auxiliary space.
    Best for: Checking individual numbers or small ranges.
    """
    
    @property
    def name(self) -> str:
        return "Trial Division (6k +/- 1)"

    def is_prime(self, n: int) -> bool:
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        
        limit = math.isqrt(n)
        for i in range(5, limit + 1, 6):
            if n % i == 0 or n % (i + 2) == 0:
                return False
        return True

    def generate_primes_in_range(self, start: int, end: int) -> List[int]:
        start = max(2, start)
        if start > end:
            return []
        return [num for num in range(start, end + 1) if self.is_prime(num)]


class ClassicSieveStrategy(PrimeAlgorithmStrategy):
    """
    Standard Sieve of Eratosthenes.
    Time Complexity: O(N log(log N))
    Space Complexity: O(N) memory
    Best for: Generating all primes up to moderate limit (up to 10^7).
    """

    @property
    def name(self) -> str:
        return "Classic Sieve of Eratosthenes"

    def _sieve_up_to(self, limit: int) -> List[bool]:
        if limit < 2:
            return [False] * (limit + 1)
        
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        
        sqrt_limit = math.isqrt(limit)
        for i in range(2, sqrt_limit + 1):
            if is_prime[i]:
                for j in range(i * i, limit + 1, i):
                    is_prime[j] = False
        return is_prime

    def generate_primes_in_range(self, start: int, end: int) -> List[int]:
        if end < 2 or start > end:
            return []
        
        max_bound = min(end, 10_000_000)
        sieve = self._sieve_up_to(max_bound)
        
        lower = max(2, start)
        return [num for num in range(lower, max_bound + 1) if sieve[num]]

    def is_prime(self, n: int) -> bool:
        if n < 2:
            return False
        if n <= 100_000:
            sieve = self._sieve_up_to(n)
            return sieve[n]
        return TrialDivisionStrategy().is_prime(n)


class SegmentedSieveStrategy(PrimeAlgorithmStrategy):
    """
    Segmented Sieve of Eratosthenes for arbitrary [L, R] ranges.
    Finds primes in [start, end] in segments of size sqrt(end), using O(sqrt(end)) auxiliary memory.
    Time Complexity: O((end - start + 1) log(log end))
    Space Complexity: O(sqrt(end) + segment_size)
    Best for: Large upper bounds and localized ranges [start, end].
    """

    @property
    def name(self) -> str:
        return "Segmented Sieve of Eratosthenes"

    def _simple_sieve(self, limit: int) -> List[int]:
        if limit < 2:
            return []
        mark = [True] * (limit + 1)
        mark[0] = mark[1] = False
        for i in range(2, math.isqrt(limit) + 1):
            if mark[i]:
                for j in range(i * i, limit + 1, i):
                    mark[j] = False
        return [i for i in range(2, limit + 1) if mark[i]]

    def generate_primes_in_range(self, start: int, end: int) -> List[int]:
        if end < 2 or start > end:
            return []
        
        low = max(2, start)
        high = end
        
        sqrt_high = math.isqrt(high)
        base_primes = self._simple_sieve(sqrt_high)
        
        segment_size = max(100_000, sqrt_high)
        result: List[int] = []
        
        current_low = low
        while current_low <= high:
            current_high = min(current_low + segment_size - 1, high)
            seg_len = current_high - current_low + 1
            is_prime = [True] * seg_len
            
            for p in base_primes:
                first_multiple = (current_low // p) * p
                if first_multiple < current_low:
                    first_multiple += p
                if first_multiple == p:
                    first_multiple += p
                
                for mult in range(first_multiple, current_high + 1, p):
                    is_prime[mult - current_low] = False
                    
            for i in range(seg_len):
                num = current_low + i
                if is_prime[i] and num >= 2:
                    result.append(num)
                    
            current_low = current_high + 1
            
        return result

    def is_prime(self, n: int) -> bool:
        if n < 2:
            return False
        return TrialDivisionStrategy().is_prime(n)


class MillerRabinStrategy(PrimeAlgorithmStrategy):
    """
    Deterministic Miller-Rabin Primality Test for 64-bit integers.
    """

    @property
    def name(self) -> str:
        return "Deterministic Miller-Rabin"

    def is_prime(self, n: int) -> bool:
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False

        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1

        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        for a in bases:
            if a >= n:
                continue
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    def generate_primes_in_range(self, start: int, end: int) -> List[int]:
        low = max(2, start)
        return [i for i in range(low, end + 1) if self.is_prime(i)]


class PrimeEngineFactory:
    """Factory and Dispatcher for Prime Algorithms"""
    
    _strategies: Dict[str, PrimeAlgorithmStrategy] = {
        "segmented": SegmentedSieveStrategy(),
        "sieve": ClassicSieveStrategy(),
        "trial": TrialDivisionStrategy(),
        "miller_rabin": MillerRabinStrategy()
    }

    @classmethod
    def get_strategy(cls, algo_type: str = "segmented") -> PrimeAlgorithmStrategy:
        key = algo_type.lower().strip()
        if key not in cls._strategies:
            return cls._strategies["segmented"]
        return cls._strategies[key]

    @classmethod
    def benchmark_all(cls, start: int, end: int) -> List[Dict[str, Any]]:
        results = []
        for key, strategy in cls._strategies.items():
            t0 = time.perf_counter()
            primes = strategy.generate_primes_in_range(start, end)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            
            results.append({
                "algorithm_key": key,
                "algorithm_name": strategy.name,
                "count": len(primes),
                "execution_time_ms": round(elapsed_ms, 3),
                "sample_first_5": primes[:5],
                "sample_last_5": primes[-5:] if len(primes) >= 5 else primes
            })
        return sorted(results, key=lambda x: x["execution_time_ms"])
