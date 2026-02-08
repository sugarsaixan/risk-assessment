"""Processing logic for creating assessments and sending SMS."""

import asyncio
import sys
from pathlib import Path
from typing import Callable

# Handle both relative and absolute imports
try:
    from .assessment_service import AssessmentService
    from .config import Configuration
    from .models import ErrorStage, ErrorType, ProcessingResult, ProcessingStatus, ProcessingSummary
    from .sms_service import SMSService
    from .validators import validate_phone_number
except ImportError:
    scripts_dir = Path(__file__).parent
    backend_dir = scripts_dir.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from scripts.assessment_service import AssessmentService
    from scripts.config import Configuration
    from scripts.models import ErrorStage, ErrorType, ProcessingResult, ProcessingStatus, ProcessingSummary
    from scripts.sms_service import SMSService
    from scripts.validators import validate_phone_number


async def process_single_phone_number(
    phone_number: str,
    config: Configuration,
    assessment_service: AssessmentService,
    sms_service: SMSService,
    verbose: bool = False,
) -> ProcessingResult:
    """Process a single phone number: validate, create assessment, send SMS.

    Args:
        phone_number: Raw phone number from input
        config: Configuration object
        assessment_service: Assessment service instance
        sms_service: SMS service instance
        verbose: Whether to log detailed information

    Returns:
        ProcessingResult with outcome
    """
    original_number = phone_number
    retry_count = 0

    # Step 1: Validate phone number
    is_valid, normalized_or_error = validate_phone_number(phone_number)

    if not is_valid:
        return ProcessingResult(
            phone_number=original_number,
            status=ProcessingStatus.FAILED_VALIDATION,
            error_message=normalized_or_error,  # Contains error message
            error_stage=ErrorStage.VALIDATION,
            error_type=ErrorType.VALIDATION_ERROR,
            retry_count=retry_count,
        )

    normalized_number = normalized_or_error  # Validated phone number

    # Step 2: Create assessment
    try:
        assessment = await assessment_service.create_assessment()

        if verbose:
            print(f"✓ Assessment created: {assessment.id}")
    except Exception as e:
        error_msg = str(e)
        if verbose:
            print(f"✗ Assessment creation failed: {error_msg}")

        # Determine error type
        error_type = ErrorType.API_ERROR
        if "Network" in type(e).__name__:
            error_type = ErrorType.NETWORK_ERROR
        elif "rate limit" in error_msg.lower():
            error_type = ErrorType.RATE_LIMIT

        return ProcessingResult(
            phone_number=original_number,
            status=ProcessingStatus.FAILED_ASSESSMENT,
            error_message=error_msg,
            error_stage=ErrorStage.ASSESSMENT,
            error_type=error_type,
            retry_count=retry_count,
        )

    # Step 3: Send SMS with assessment URL
    try:
        # Format message with URL
        message = config.message_template.format(url=assessment.url)

        sms_response = await sms_service.send_sms(
            to=normalized_number,
            message=message,
        )

        if verbose:
            print(f"✓ SMS sent to {normalized_number}")

        if not sms_response.is_successful():
            return ProcessingResult(
                phone_number=original_number,
                status=ProcessingStatus.FAILED_SMS,
                error_message=f"SMS API returned: {sms_response.status}",
                error_stage=ErrorStage.SMS,
                error_type=ErrorType.API_ERROR,
                assessment_id=assessment.id,
                assessment_url=assessment.url,
                retry_count=retry_count,
            )

    except Exception as e:
        error_msg = str(e)
        if verbose:
            print(f"✗ SMS send failed: {error_msg}")

        # Determine error type
        error_type = ErrorType.API_ERROR
        if "Network" in type(e).__name__:
            error_type = ErrorType.NETWORK_ERROR
        elif "rate limit" in error_msg.lower():
            error_type = ErrorType.RATE_LIMIT

        return ProcessingResult(
            phone_number=original_number,
            status=ProcessingStatus.FAILED_SMS,
            error_message=error_msg,
            error_stage=ErrorStage.SMS,
            error_type=error_type,
            assessment_id=assessment.id,
            assessment_url=assessment.url,
            retry_count=retry_count,
        )

    # Success!
    return ProcessingResult(
        phone_number=original_number,
        status=ProcessingStatus.SUCCESS,
        assessment_id=assessment.id,
        assessment_url=assessment.url,
        retry_count=retry_count,
    )


async def process_phone_numbers_batch(
    phone_numbers: list[str],
    config: Configuration,
    assessment_service: AssessmentService,
    sms_service: SMSService,
    verbose: bool = False,
    progress_callback: Callable[[int, int], None] | None = None,
) -> ProcessingSummary:
    """Process multiple phone numbers concurrently with continue-on-error.

    Args:
        phone_numbers: List of phone numbers to process
        config: Configuration object
        assessment_service: Assessment service instance
        sms_service: SMS service instance
        verbose: Whether to log detailed information
        progress_callback: Optional callback for progress updates (current, total)

    Returns:
        ProcessingSummary with all results
    """
    summary = ProcessingSummary()

    # Create semaphore for concurrency limiting
    semaphore = asyncio.Semaphore(config.processing.max_concurrent)

    async def process_with_limit(phone_number: str, index: int) -> ProcessingResult:
        """Process one phone number with semaphore limiting."""
        async with semaphore:
            if progress_callback:
                progress_callback(index + 1, len(phone_numbers))

            return await process_single_phone_number(
                phone_number=phone_number,
                config=config,
                assessment_service=assessment_service,
                sms_service=sms_service,
                verbose=verbose,
            )

    # Create tasks for all phone numbers
    tasks = [
        process_with_limit(phone_number, i)
        for i, phone_number in enumerate(phone_numbers)
    ]

    # Process all concurrently, collecting results as they complete
    results = await asyncio.gather(*tasks, return_exceptions=False)

    # Add all results to summary
    for result in results:
        summary.add_result(result)

    return summary
