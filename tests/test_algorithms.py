"""Unit Tests for Prime Generation Algorithms"""
import pytest
from app.algorithms import (
    TrialDivisionStrategy, ClassicSieveStrategy,
    SegmentedSieveStrategy, MillerRabinStrategy
)

KNOWN_PRIMES_UP_TO_30 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


@pytest.mark.parametrize("strategy", [
    TrialDivisionStrategy(),
    ClassicSieveStrategy(),
    SegmentedSieveStrategy(),
    MillerRabinStrategy()
])
def test_range_generation(strategy):
    primes = strategy.generate_primes_in_range(1, 30)
    assert primes == KNOWN_PRIMES_UP_TO_30


@pytest.mark.parametrize("strategy", [
    TrialDivisionStrategy(),
    ClassicSieveStrategy(),
    SegmentedSieveStrategy(),
    MillerRabinStrategy()
])
def test_edge_cases(strategy):
    assert strategy.generate_primes_in_range(-10, 1) == []
    assert strategy.generate_primes_in_range(0, 0) == []
    assert strategy.generate_primes_in_range(10, 5) == []


@pytest.mark.parametrize("strategy", [
    TrialDivisionStrategy(),
    ClassicSieveStrategy(),
    SegmentedSieveStrategy(),
    MillerRabinStrategy()
])
def test_is_prime_validation(strategy):
    assert strategy.is_prime(2) is True
    assert strategy.is_prime(3) is True
    assert strategy.is_prime(4) is False
    assert strategy.is_prime(17) is True
    assert strategy.is_prime(100) is False
    assert strategy.is_prime(1000000007) is True  # Large prime
