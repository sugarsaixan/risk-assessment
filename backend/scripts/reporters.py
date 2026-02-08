"""Report formatters for processing results."""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import TextIO

# Handle both relative and absolute imports
try:
    from .models import ProcessingResult, ProcessingSummary
except ImportError:
    scripts_dir = Path(__file__).parent
    backend_dir = scripts_dir.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from scripts.models import ProcessingResult, ProcessingSummary


def generate_console_report(summary: ProcessingSummary, output: TextIO | None = None) -> None:
    """Generate a human-readable console report.

    Args:
        summary: Processing summary with results
        output: Output stream (defaults to stdout)
    """
    if output is None:
        import sys

        output = sys.stdout

    # Header
    output.write("\n")
    output.write("=" * 60 + "\n")
    output.write("Processing Summary\n")
    output.write("=" * 60 + "\n")
    output.write(f"Total phone numbers: {summary.total_count}\n")
    output.write(f"Successfully processed: {summary.success_count}\n")
    output.write(f"Failed: {summary.failure_count}\n")
    if summary.start_time and summary.end_time:
        output.write(f"Duration: {summary.duration_seconds:.1f} seconds\n")
    output.write("\n")

    # Success details
    if summary.success_count > 0:
        output.write("Success Details:\n")
        for result in summary.results:
            if result.status.value == "SUCCESS":
                output.write(
                    f"✓ {result.phone_number}: "
                    f"Assessment created (ID: {result.assessment_id}), SMS sent\n"
                )
        output.write("\n")

    # Failure details
    if summary.failure_count > 0:
        output.write("Failure Details:\n")
        for result in summary.results:
            if result.status.value != "SUCCESS":
                output.write(
                    f"✗ {result.phone_number}: {result.error_message} "
                    f"({result.error_stage.value if result.error_stage else 'Unknown'})\n"
                )
        output.write("\n")

    # Footer
    if summary.failure_count == 0:
        output.write("All done! 🎉\n")
    else:
        output.write(f"Completed with {summary.failure_count} error(s)\n")
    output.write("\n")


def generate_json_report(summary: ProcessingSummary, output_file: str | Path) -> None:
    """Generate a machine-readable JSON report.

    Args:
        summary: Processing summary with results
        output_file: Path to output JSON file
    """
    output_path = Path(output_file)

    # Build JSON structure
    report_data = {
        "summary": {
            "total_count": summary.total_count,
            "success_count": summary.success_count,
            "failure_count": summary.failure_count,
            "duration_seconds": round(summary.duration_seconds, 2),
        },
        "results": [],
    }

    # Add results
    for result in summary.results:
        result_data = {
            "phone_number": result.phone_number,
            "status": result.status.value,
        }

        if result.status.value == "SUCCESS":
            result_data["assessment_id"] = result.assessment_id
            result_data["assessment_url"] = result.assessment_url
        else:
            result_data["error_message"] = result.error_message
            if result.error_stage:
                result_data["error_stage"] = result.error_stage.value
            if result.error_type:
                result_data["error_type"] = result.error_type.value

        result_data["timestamp"] = result.timestamp.isoformat()
        report_data["results"].append(result_data)

    # Write to file
    with open(output_path, "w") as f:
        json.dump(report_data, f, indent=2)


def generate_csv_report(summary: ProcessingSummary, output_file: str | Path) -> None:
    """Generate a spreadsheet-compatible CSV report.

    Args:
        summary: Processing summary with results
        output_file: Path to output CSV file
    """
    output_path = Path(output_file)

    # CSV columns
    fieldnames = [
        "phone_number",
        "status",
        "assessment_id",
        "assessment_url",
        "error_message",
        "error_stage",
        "error_type",
        "timestamp",
    ]

    # Write to file
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in summary.results:
            row = {
                "phone_number": result.phone_number,
                "status": result.status.value,
                "assessment_id": result.assessment_id or "",
                "assessment_url": result.assessment_url or "",
                "error_message": result.error_message or "",
                "error_stage": result.error_stage.value if result.error_stage else "",
                "error_type": result.error_type.value if result.error_type else "",
                "timestamp": result.timestamp.isoformat(),
            }
            writer.writerow(row)
