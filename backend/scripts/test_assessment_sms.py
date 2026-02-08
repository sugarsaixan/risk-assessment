#!/usr/bin/env python3
"""Test Assessment SMS Distribution Tool - Main CLI.

This script creates risk assessments and sends SMS invitations to test users.

Usage from backend directory:
    uv run python scripts/test_assessment_sms.py phone_numbers.txt --dry-run
    python -m scripts.test_assessment_sms phone_numbers.txt --dry-run
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Handle both direct execution (uv run python) and module execution
try:
    from .assessment_service import AssessmentService
    from .config import Configuration, load_config
    from .exceptions import BaseScriptException, ConfigurationException
    from .models import ProcessingSummary
    from .processor import process_phone_numbers_batch
    from .reporters import generate_console_report, generate_csv_report, generate_json_report
    from .sms_service import SMSService
except ImportError:
    # Running as script directly - add parent dir and use absolute imports
    scripts_dir = Path(__file__).parent
    backend_dir = scripts_dir.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from scripts.assessment_service import AssessmentService
    from scripts.config import Configuration, load_config
    from scripts.exceptions import BaseScriptException, ConfigurationException
    from scripts.models import ProcessingSummary
    from scripts.processor import process_phone_numbers_batch
    from scripts.reporters import generate_console_report, generate_csv_report, generate_json_report
    from scripts.sms_service import SMSService


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="test_assessment_sms",
        description="Send assessment invitations via SMS to test users",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input_file",
        help="File containing phone numbers (one per line)",
    )

    parser.add_argument(
        "--config",
        default=None,
        help="Path to config file (default: backend/scripts/config.yml)",
    )

    parser.add_argument(
        "--output-format",
        choices=["console", "json", "csv"],
        default="console",
        help="Output format (default: console)",
    )

    parser.add_argument(
        "--output-file",
        default=None,
        help="Path to output file (required for json/csv formats)",
    )

    parser.add_argument(
        "--respondent-id",
        default=None,
        help="Override default respondent ID",
    )

    parser.add_argument(
        "--type-ids",
        default=None,
        help="Comma-separated list of assessment type IDs",
    )

    parser.add_argument(
        "--expires-in-days",
        type=int,
        default=None,
        help="Assessment expiration in days (default: 30)",
    )

    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=None,
        help="Maximum concurrent API requests (default: 10)",
    )

    parser.add_argument(
        "--retry-attempts",
        type=int,
        default=None,
        help="Number of retry attempts (default: 2)",
    )

    parser.add_argument(
        "--retry-delay-seconds",
        type=int,
        default=None,
        help="Delay between retries in seconds (default: 5)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input without sending",
    )

    return parser.parse_args()


def read_phone_numbers(input_file: str) -> list[str]:
    """Read phone numbers from input file.

    Args:
        input_file: Path to input file

    Returns:
        List of phone numbers (one per line, comments and blanks filtered out)

    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    phone_numbers = []
    with open(input_path) as f:
        for line in f:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comments
            if line.startswith("#"):
                continue

            phone_numbers.append(line)

    return phone_numbers


async def main() -> int:
    """Main entry point for the script.

    Returns:
        Exit code (0 for success, non-zero for failures)
    """
    args = parse_arguments()

    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    # Override config with CLI arguments
    if args.respondent_id:
        config.assessment_api.respondent_id = args.respondent_id
    if args.type_ids:
        config.assessment_api.selected_type_ids = args.type_ids.split(",")
    if args.expires_in_days is not None:
        config.assessment_api.expires_in_days = args.expires_in_days
    if args.max_concurrent is not None:
        config.processing.max_concurrent = args.max_concurrent
    if args.retry_attempts is not None:
        config.processing.retry_attempts = args.retry_attempts
    if args.retry_delay_seconds is not None:
        config.processing.retry_delay_seconds = args.retry_delay_seconds

    # Read phone numbers from input file
    try:
        phone_numbers = read_phone_numbers(args.input_file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not phone_numbers:
        print("Error: No phone numbers found in input file", file=sys.stderr)
        return 1

    # Dry run mode - just validate
    if args.dry_run:
        print(f"Dry run mode - validating {len(phone_numbers)} phone numbers...\n")

        from .validators import validate_phone_number

        valid_count = 0
        invalid_count = 0

        for phone_number in phone_numbers:
            is_valid, result = validate_phone_number(phone_number)
            if is_valid:
                print(f"✓ {phone_number} → {result}")
                valid_count += 1
            else:
                print(f"✗ {phone_number} → {result}")
                invalid_count += 1

        print(f"\nValid: {valid_count}, Invalid: {invalid_count}")

        return 0 if invalid_count == 0 else 1

    # Initialize services
    assessment_service = AssessmentService(config)
    sms_service = SMSService(config)

    # Progress callback for showing progress
    def show_progress(current: int, total: int) -> None:
        """Show progress indicator if not verbose."""
        if not args.verbose:
            print(f"[{current}/{total}] Processing...", end="\r")

    # Process phone numbers (with concurrent batch processing)
    try:
        summary = await process_phone_numbers_batch(
            phone_numbers=phone_numbers,
            config=config,
            assessment_service=assessment_service,
            sms_service=sms_service,
            verbose=args.verbose,
            progress_callback=show_progress if not args.verbose else None,
        )
    except Exception as e:
        print(f"\nError during processing: {e}", file=sys.stderr)
        return 1

    print()  # New line after progress indicator

    # Generate report
    if args.output_format == "console":
        generate_console_report(summary)
    elif args.output_format == "json":
        if not args.output_file:
            print("Error: --output-file required for JSON format", file=sys.stderr)
            return 1
        generate_json_report(summary, args.output_file)
        print(f"JSON report written to: {args.output_file}")
    elif args.output_format == "csv":
        if not args.output_file:
            print("Error: --output-file required for CSV format", file=sys.stderr)
            return 1
        generate_csv_report(summary, args.output_file)
        print(f"CSV report written to: {args.output_file}")

    # Exit with non-zero if any failures
    return 0 if summary.failure_count == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        sys.exit(1)
