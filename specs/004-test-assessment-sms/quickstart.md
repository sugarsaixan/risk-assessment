# Quickstart Guide: Test Assessment SMS Distribution Tool

**Feature**: 004-test-assessment-sms
**Date**: 2026-02-04

## Overview

This guide helps you quickly set up and use the test assessment SMS distribution tool, which creates risk assessments and sends invitation links via SMS to test users.

## Prerequisites

- Python 3.11 or higher
- Access to assessment API (API key and session ID)
- Access to SMS API (API key)
- Phone numbers for test users

## Installation

### 1. Set Up Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -e .
```

### 2. Set Up API Keys

Create a `.env` file in the project root (or update existing one):

```bash
# Assessment API Credentials
ASSESSMENT_API_KEY=bulm8dhUuBVk5nxrrqG4DILeytSJSYsI3rY_07fXboc
ASSESSMENT_SESSION_ID=f3b5afc2df06cd0d7b130eb2401e150b956379ce

# SMS API Credentials
SMS_API_KEY=QUspgvkssiTFJNyoY6Tw
```

**Important**: Never commit `.env` to version control!

### 3. Create Configuration File

Copy the template and customize:

```bash
cp backend/scripts/config_template.yml backend/scripts/config.yml
```

Edit `config.yml` to set your defaults:

```yaml
assessment_api:
  base_url: "https://aisys.agula.mn"
  api_key: "${ASSESSMENT_API_KEY}"
  session_id: "${ASSESSMENT_SESSION_ID}"
  respondent_id: "1a6f1659-9f6a-4553-bdf2-399ac193a2b3"
  selected_type_ids:
    - "16ed991d-5239-421d-a5f2-871e5cfabf3e"
    - "46288660-9e9e-42f6-8d25-5f1dbef0103a"
  expires_in_days: 30

sms_api:
  base_url: "https://sms.agula.mn"
  api_key: "${SMS_API_KEY}"

message_template: "Sain baina uu. Ersdeliiin unelgeenii asuulga bogloh holboos: {url}"

processing:
  max_concurrent: 10
  retry_attempts: 2
  retry_delay_seconds: 5
```

## Basic Usage

### 1. Prepare Phone Numbers

Create a text file with one phone number per line:

```bash
# test_users.txt
89113840
89113841
89113842
```

**Notes**:
- Lines starting with `#` are comments
- Blank lines are ignored
- Mongolian phone numbers: 8 digits starting with 8 or 9
- Can include country code: +976 8911-3840

### 2. Run the Script

```bash
python backend/scripts/test_assessment_sms.py test_users.txt
```

### 3. View Results

The script will output:

```
Test Assessment SMS Distribution Tool
======================================

Configuration:
- Assessment API: https://aisys.agula.mn
- SMS API: https://sms.agula.mn
- Max concurrent: 10

Processing 3 phone numbers...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 3/3

Processing Summary
==================
Total phone numbers: 3
Successfully processed: 3
Failed: 0
Duration: 12.5 seconds

Success Details:
✓ 89113840: Assessment created (ID: 20ebdd4c-a5ba-4616-a32c-d4739fe38ba2), SMS sent
✓ 89113841: Assessment created (ID: 21ebdd4c-a5ba-4616-a32c-d4739fe38ba2), SMS sent
✓ 89113842: Assessment created (ID: 22ebdd4c-a5ba-4616-a32c-d4739fe38ba2), SMS sent

All done!
```

## Advanced Usage

### Custom Output Format

Generate JSON report for automation:

```bash
python backend/scripts/test_assessment_sms.py test_users.txt \
  --output-format json \
  --output-file results.json
```

Generate CSV report for spreadsheets:

```bash
python backend/scripts/test_assessment_sms.py test_users.txt \
  --output-format csv \
  --output-file results.csv
```

### Override Configuration

Customize respondent and assessment types:

```bash
python backend/scripts/test_assessment_sms.py test_users.txt \
  --respondent-id "new-respondent-uuid" \
  --type-ids "type-uuid-1,type-uuid-2"
```

Adjust concurrency for rate limits:

```bash
python backend/scripts/test_assessment_sms.py test_users.txt \
  --max-concurrent 5
```

### Verbose Output

Show detailed per-number processing:

```bash
python backend/scripts/test_assessment_sms.py test_users.txt --verbose
```

### Dry Run

Validate phone numbers without sending:

```bash
python backend/scripts/test_assessment_sms.py test_users.txt --dry-run
```

## Command-Line Options

```
usage: test_assessment_sms.py [-h] [--config CONFIG] [--output-format {console,json,csv}]
                              [--output-file OUTPUT_FILE] [--respondent-id RESPONDENT_ID]
                              [--type-ids TYPE_IDS] [--expires-in-days EXPIRES_IN_DAYS]
                              [--max-concurrent MAX_CONCURRENT] [--retry-attempts RETRY_ATTEMPTS]
                              [--retry-delay-seconds RETRY_DELAY_SECONDS] [--verbose] [--dry-run]
                              input_file

Send assessment invitations via SMS to test users

positional arguments:
  input_file            File containing phone numbers (one per line)

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to config file (default: backend/scripts/config.yml)
  --output-format {console,json,csv}
                        Output format (default: console)
  --output-file OUTPUT_FILE
                        Path to output file (required for json/csv formats)
  --respondent-id RESPONDENT_ID
                        Override default respondent ID
  --type-ids TYPE_IDS   Comma-separated list of assessment type IDs
  --expires-in-days EXPIRES_IN_DAYS
                        Assessment expiration in days (default: 30)
  --max-concurrent MAX_CONCURRENT
                        Maximum concurrent API requests (default: 10)
  --retry-attempts RETRY_ATTEMPTS
                        Number of retry attempts (default: 2)
  --retry-delay-seconds RETRY_DELAY_SECONDS
                        Delay between retries in seconds (default: 5)
  --verbose, -v         Show detailed output
  --dry-run             Validate input without sending
```

## Troubleshooting

### "Invalid phone number format"

Ensure phone numbers are:
- 8 digits long for Mongolian numbers
- Starting with 8 or 9
- Without spaces or special characters (script will normalize)

### "API key not found"

Check that:
- `.env` file exists in project root
- Environment variables are set correctly
- `config.yml` references the correct variable names

### "Rate limit exceeded"

Reduce concurrency:
```bash
python backend/scripts/test_assessment_sms.py test_users.txt --max-concurrent 3
```

### "Assessment creation failed"

Check:
- Assessment API is accessible
- API key and session ID are valid
- Respondent ID exists in the system
- Assessment type IDs are valid

### "SMS send failed"

Check:
- SMS API is accessible
- API key is valid
- Sufficient SMS credits available
- Phone number format is correct

## Testing

### Test with One Number

Create a test file with your own phone number:

```bash
echo "89113840" > my_number.txt
python backend/scripts/test_assessment_sms.py my_number.txt
```

### Dry Run Mode

Validate everything without sending:

```bash
python backend/scripts/test_assessment_sms.py test_users.txt --dry-run
```

### Verbose Mode

See all API calls and responses:

```bash
python backend/scripts/test_assessment_sms.py test_users.txt --verbose
```

## Examples

### Example 1: Send to 5 Test Users

```bash
echo -e "89113840\n89113841\n89113842\n89113843\n89113844" > test.txt
python backend/scripts/test_assessment_sms.py test.txt
```

### Example 2: Generate CSV Report

```bash
python backend/scripts/test_assessment_sms.py test_users.txt \
  --output-format csv \
  --output-file report_$(date +%Y%m%d).csv
```

### Example 3: Custom Assessment Configuration

```bash
python backend/scripts/test_assessment_sms.py test_users.txt \
  --respondent-id "custom-respondent-uuid" \
  --type-ids "custom-type-1,custom-type-2" \
  --expires-in-days 60
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Send Test Invitations
on:
  workflow_dispatch:
    inputs:
      phone_file:
        description: 'Phone numbers file'
        required: true

jobs:
  send:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -e .
      - name: Send invitations
        env:
          ASSESSMENT_API_KEY: ${{ secrets.ASSESSMENT_API_KEY }}
          SMS_API_KEY: ${{ secrets.SMS_API_KEY }}
        run: |
          python backend/scripts/test_assessment_sms.py \
            ${{ inputs.phone_file }} \
            --output-format json \
            --output-file results.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: results
          path: results.json
```

## Support

For issues or questions:
1. Check the logs with `--verbose` flag
2. Review API credentials in `.env`
3. Verify configuration in `config.yml`
4. Check API service availability
5. Review error messages in console output

## Next Steps

- Customize the message template for your needs
- Set up scheduled runs for regular test campaigns
- Integrate with your existing testing workflow
- Add phone number validation for your region
