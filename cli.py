"""
Command-Line Interface (CLI) for Prime Generator Engine
Usage:
    # Direct positional range generation (as requested in assignment):
    python cli.py 1 10
    python cli.py 1 100 --algo sieve

    # Subcommand based usage:
    python cli.py range --start 1 --end 100 --algo segmented
    python cli.py check 1000000007
    python cli.py benchmark --start 1 --end 50000
"""
import argparse
import sys
from app.algorithms import PrimeEngineFactory


def format_primes(primes: list, max_display: int = 50) -> str:
    """Format prime list cleanly, e.g. 2, 3, 5, 7"""
    if len(primes) <= max_display:
        return ", ".join(map(str, primes))
    head = ", ".join(map(str, primes[:max_display]))
    return f"{head} ... (+{len(primes) - max_display} more primes)"


def handle_direct_range(args_list):
    """Handle direct syntax: python cli.py 1 10 [--algo ALGO]"""
    parser = argparse.ArgumentParser(description="Generate primes between two numbers")
    parser.add_argument("start", type=int, help="Start number")
    parser.add_argument("end", type=int, help="End number")
    parser.add_argument("--algo", "-a", type=str, default="segmented",
                        choices=["segmented", "sieve", "trial", "miller_rabin"],
                        help="Algorithm strategy (default: segmented)")
    
    args = parser.parse_args(args_list)
    strategy = PrimeEngineFactory.get_strategy(args.algo)
    primes = strategy.generate_primes_in_range(args.start, args.end)
    print(f"\n[+] Prime numbers in range [{args.start}, {args.end}] using {strategy.name}:")
    print(f"    Count : {len(primes)}")
    print(f"    Primes: {format_primes(primes)}\n")


def main():
    raw_args = sys.argv[1:]
    
    # If called with positional numbers directly: e.g. python cli.py 1 10
    if len(raw_args) >= 2 and raw_args[0].lstrip("-").isdigit() and raw_args[1].lstrip("-").isdigit():
        handle_direct_range(raw_args)
        return

    parser = argparse.ArgumentParser(
        description="Prime Number Generator Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: range
    range_parser = subparsers.add_parser("range", help="Generate primes in a range [start, end]")
    range_parser.add_argument("--start", "-s", type=int, default=1, help="Start range (default: 1)")
    range_parser.add_argument("--end", "-e", type=int, required=True, help="End range (e.g. 100)")
    range_parser.add_argument("--algo", "-a", type=str, default="segmented",
                              choices=["segmented", "sieve", "trial", "miller_rabin"],
                              help="Algorithm strategy (default: segmented)")

    # Command: check
    check_parser = subparsers.add_parser("check", help="Check if a single number is prime")
    check_parser.add_argument("number", type=int, help="The number to check")
    check_parser.add_argument("--algo", "-a", type=str, default="miller_rabin",
                              choices=["miller_rabin", "trial"], help="Algorithm to test")

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Benchmark all algorithms on a range")
    bench_parser.add_argument("--start", "-s", type=int, default=1)
    bench_parser.add_argument("--end", "-e", type=int, default=100000)

    if len(raw_args) == 0:
        parser.print_help()
        print("\nQuick Example:")
        print("  python cli.py 1 10")
        print("  python cli.py range --start 1 --end 100 --algo segmented\n")
        sys.exit(0)

    args = parser.parse_args(raw_args)

    if args.command == "range":
        strategy = PrimeEngineFactory.get_strategy(args.algo)
        primes = strategy.generate_primes_in_range(args.start, args.end)
        print(f"\n[+] Generated {len(primes)} primes in [{args.start}, {args.end}] using {strategy.name}:")
        print(f"    {format_primes(primes)}\n")

    elif args.command == "check":
        strategy = PrimeEngineFactory.get_strategy(args.algo)
        is_p = strategy.is_prime(args.number)
        status = "is a PRIME NUMBER!" if is_p else "is NOT a prime number."
        print(f"\n>> Result: {args.number} {status} (Evaluated with {strategy.name})\n")

    elif args.command == "benchmark":
        print(f"\n[*] Running benchmark comparison on [{args.start}, {args.end}]...\n")
        results = PrimeEngineFactory.benchmark_all(args.start, args.end)
        print(f"{'Rank':<6} | {'Algorithm':<35} | {'Count':<10} | {'Time (ms)':<12}")
        print("-" * 70)
        for i, r in enumerate(results, 1):
            print(f"{i:<6} | {r['algorithm_name']:<35} | {r['count']:<10} | {r['execution_time_ms']:<12.3f}")
        print()


if __name__ == "__main__":
    main()
