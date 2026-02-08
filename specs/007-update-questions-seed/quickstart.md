# Quickstart Guide: Questions Seed with Custom Scoring

**Feature**: 007-update-questions-seed
**Last Updated**: 2026-02-08

## Overview

This guide shows developers how to update question markdown files with custom scoring and run the seed script to import them into the database.

## Prerequisites

- Python 3.11+ installed
- PostgreSQL database running
- Backend dependencies installed: `pip install -r requirements.txt`
- Database models migrated: `alembic upgrade head`

## Step 1: Prepare Question Markdown Files

### File Location

Place markdown files in the `questions/` folder at project root:

```text
risk-assessment/
├── questions/
│   ├── fire_safety.md
│   ├── electrical_safety.md
│   └── occupational_safety.md
├── backend/
└── frontend/
```

### File Format

Each markdown file follows this structure:

```markdown
Type Name (e.g., ГАЛЫН АЮУЛГҮЙ БАЙДАЛ)
    Group Name (e.g., Галын хор)
        Question text in Mongolian        Үгүй    1
        Another question        Тийм    0
    Another Group
        Question text    Үгүй    1
```

**Format Rules**:
- **Type Header**: No indentation, ends with colon (optional)
- **Group Header**: 4-space indent or 1-tab, ends with colon (optional)
- **Question Line**: 8-space indent or 2-tab, 3 parts separated by whitespace:
  1. Question text (can contain spaces)
  2. Option text: `Үгүй` or `Тийм`
  3. Score: `0` or `1`

**Inverse Scoring Logic**:
- If `Үгүй` has score `1`, then `Тийм` automatically gets score `0`
- If `Тийм` has score `1`, then `Үгүй` automatically gets score `0`
- Both can have score `0` (neither option indicates an issue)

### Example: Complete Markdown File

Create `questions/fire_safety.md`:

```markdown
ГАЛЫН АЮУЛГҮЙ БАЙДАЛ
    Галын хор
        Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх        Үгүй    1
        Монометр нь ногоон түвшинг зааж байгаа эсэх        Үгүй    1
        Галын хорыг сүүлийн 6 сарын дотор туршиж үзсэн эсэх        Үгүй    1
        Галын хорын ангилал нь тухайн байгууламжид тохирох эсэх        Үгүй    1
        Галын хорын тэмдэг, тэмдэглэгээ байгаа эсэх        Үгүй    1
    Галд шатах материал
        Галд шатах материалууд дийлэнх хувийг эзэлдэг эсэх        Үгүй    1
        Шатах материалыг 3 метрээс дээш өндөрт хураасан эсэх        Үгүй    1
        Цахилгааны залгуур, өндөр хүчдэлийг налуулан бараа материал хураасан эсэх        Үгүй    1
        Тухайн бараа материал, үхэлд хүргэх химийн хорт хий ялгаруулдаг эсэх        Тийм    0
        Тухайн бараа материал галд тэсвэргүй, хурдан шатамхай эсэх        Үгүй    1
```

**Key Points**:
- UTF-8 encoding required (for Mongolian Cyrillic text)
- Empty lines separate sections
- Lines starting with `#` are treated as comments
- Extra whitespace is acceptable (stripped during parsing)

## Step 2: Run the Seed Script

### Basic Usage

From the project root:

```bash
cd backend
python -m src.seeds.questions_seed
```

### Expected Output

```
Starting question seed...
==================================================
Created Type: ГАЛЫН АЮУЛГҮЙ БАЙДАЛ
  Created Group: Галын хор
    Created 5 questions
  Created Group: Галд шатах материал
    Created 5 questions
Created Type: ЦАХИЛГААНЫ АЮУЛГҮЙ БАЙДАЛ
  Created Group: Хэрэглэгчийн үүрэг хариуцлага
    Created 5 questions
...
==================================================
Seed completed!
  Types: 6
  Groups: 25
  Questions: 243
  Options: 486
  Errors: 0
```

### What Happens Internally

1. **Discovery**: Script finds all `*.md` files in `questions/` folder
2. **Parsing**: Each file is parsed line-by-line to extract types, groups, questions
3. **Database Operations**:
   - For each type: Create or update QuestionnaireType
   - For each group: Create or update QuestionGroup
   - For each question: Create or update Question with two QuestionOptions
4. **Inverse Scoring**: If parsed option has score 1, the other option gets score 0
5. **Summary**: Prints counts of created/updated entities

## Step 3: Verify Import

### Check Database

Query the database to verify questions were imported:

```python
# Using Python async session
from sqlalchemy import select
from src.models.question import Question
from src.models.questionnaire_type import QuestionnaireType

async with async_session_factory() as session:
    # Get all types
    result = await session.execute(select(QuestionnaireType))
    types = result.scalars().all()

    for qtype in types:
        print(f"Type: {qtype.name}")
        for group in qtype.groups:
            print(f"  Group: {group.name}")
            for question in group.questions:
                print(f"    Question: {question.text}")
                for option in question.options:
                    print(f"      {option.option_type}: score={option.score}")
```

### Check via Admin API (if available)

```bash
curl http://localhost:8000/api/admin/questionnaire-types
```

## Common Scenarios

### Scenario 1: Update Existing Questions

If questions already exist in the database:

```bash
# Edit markdown file with updated scores
vim questions/fire_safety.md

# Re-run seed script
python -m src.seeds.questions_seed
```

**Result**: Existing questions are updated, new questions are created, unchanged questions remain as-is.

### Scenario 2: Add New Questions to Existing Type

```markdown
Existing Type Name
    Existing Group
        Existing question    Үгүй    1
        New question here    Тийм    0
```

**Result**: New question is added, existing question remains unchanged.

### Scenario 3: Create New Type with Groups

Add a new markdown file or append to existing file:

```markdown
NEW TYPE NAME
    New Group Name
        First question    Үгүй    1
        Second question    Тийм    0
```

**Result**: New QuestionnaireType and QuestionGroup are created.

## Error Handling

### Common Errors and Solutions

#### Error: `UnicodeDecodeError: 'utf-8' codec can't decode byte`

**Cause**: Markdown file not saved as UTF-8

**Solution**:
```bash
# Convert file to UTF-8
iconv -f LATIN-1 -t UTF-8 input.md > output.md

# Or save file as UTF-8 from your text editor
```

#### Error: `ValueError: Invalid score '2' (must be 0 or 1)`

**Cause**: Score value is not 0 or 1

**Solution**: Edit markdown file, ensure score is 0 or 1

#### Warning: `Question line missing score, using default 0`

**Cause**: Question line doesn't have score value

**Solution**: Add score value to question line

#### Error: `FileNotFoundError: questions/ folder does not exist`

**Cause**: questions folder missing

**Solution**:
```bash
mkdir -p questions
# Place markdown files in questions/
```

## Best Practices

### 1. Use UTF-8 Encoding

Always save markdown files as UTF-8 to properly display Mongolian Cyrillic text:

```bash
# Check file encoding
file -i questions/fire_safety.md

# Convert to UTF-8 if needed
iconv -f LATIN-1 -t UTF-8 input.md > output.md
```

### 2. Organize by Risk Type

Group related questions in separate markdown files:

```text
questions/
├── fire_safety.md         # ГАЛЫН АЮУЛГҮЙ БАЙДАЛ
├── electrical_safety.md   # ЦАХИЛГААНЫ АЮУЛГҮЙ БАЙДАЛ
├── occupational_safety.md # ХӨДӨЛМӨРИЙН АЮУЛГҮЙ БАЙДАЛ
└── warehouse_safety.md    # АГУУЛАХЫН АЮУЛГҮЙ БАЙДАЛ
```

### 3. Test Import Before Production

Always test seed script on development database first:

```bash
# Use development database
export DATABASE_URL="postgresql://user:pass@localhost/dev_db"

# Run seed script
python -m src.seeds.questions_seed

# Verify output
echo $?  # Should be 0
```

### 4. Keep Backups

Backup existing questions before running seed script:

```bash
# Export existing questions to SQL
pg_dump -h localhost -U user -d risk_assessment -t questionnaire_types \
  -t question_groups -t questions -t question_options > backup.sql

# Or use Python script to export to JSON
python -m src.scripts.export_questions > backup.json
```

### 5. Validate Scores Manually

After running seed script, spot-check a few questions:

```sql
-- Check that scores match markdown file
SELECT
  qt.name AS type_name,
  qg.name AS group_name,
  q.text AS question_text,
  qo.option_type,
  qo.score
FROM questions q
JOIN question_groups qg ON q.group_id = qg.id
JOIN questionnaire_types qt ON qg.type_id = qt.id
JOIN question_options qo ON q.question_id = qo.id
WHERE qt.name = 'ГАЛЫН АЮУЛГҮЙ БАЙДАЛ'
ORDER BY qg.display_order, q.display_order, qo.option_type;
```

## Troubleshooting

### Problem: Seed script hangs

**Symptoms**: No output after "Starting question seed..."

**Possible Causes**:
1. Database connection issue
2. Lock contention on tables

**Solutions**:
```bash
# Check database connection
psql -h localhost -U user -d risk_assessment -c "SELECT 1;"

# Check for long-running queries
psql -h localhost -U user -d risk_assessment -c \
  "SELECT pid, now() - query_start as duration, query
   FROM pg_stat_activity WHERE state = 'active'
   ORDER BY duration DESC;"

# Kill long-running queries if needed
psql -h localhost -U user -d risk_assessment -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = ..."
```

### Problem: Duplicate questions created

**Symptoms**: Same question appears multiple times

**Cause**: Running seed script multiple times without unique constraints

**Solution**: Check natural key uniqueness:
```sql
-- Check for duplicate questions
SELECT text, group_id, COUNT(*) as count
FROM questions
GROUP BY text, group_id
HAVING COUNT(*) > 1;
```

### Problem: Wrong scores in database

**Symptoms**: Scores don't match markdown file

**Cause**: Inverse scoring logic applied incorrectly

**Solution**: Verify parsing logic:
```python
# Test parsing manually
from src.seeds.questions_seed import parse_markdown_file
from pathlib import Path

data = parse_markdown_file(Path("questions/fire_safety.md"))
for type_data in data.types:
    for group in type_data.groups:
        for q in group.questions:
            print(f"{q.text} | {q.option_text} | {q.score}")
```

## Performance Tips

### Speed Up Large Imports

If importing many questions (>1000), use batch operations:

```python
# In seed script, use bulk operations
from sqlalchemy import insert

# Bulk insert options
options_data = [
    {"question_id": q.id, "option_type": "NO", "score": no_score, ...},
    {"question_id": q.id, "option_type": "YES", "score": yes_score, ...},
]
await session.execute(insert(QuestionOption), options_data)
```

### Monitor Progress

For large imports, add progress indicators:

```python
import logging
logging.basicConfig(level=logging.INFO)

# In seed loop
for i, md_file in enumerate(md_files, 1):
    logging.info(f"Processing file {i}/{len(md_files)}: {md_file.name}")
```

## Advanced Usage

### Custom Database Connection

Use custom database URL:

```bash
export DATABASE_URL="postgresql://user:pass@custom-host:5432/dbname"
python -m src.seeds.questions_seed
```

### Dry-Run Mode

Parse files without database changes (for testing):

```python
# Modify seed script to skip session.commit()
async def seed_questions(session: AsyncSession, dry_run: bool = False):
    # ... parsing and creation logic ...
    if not dry_run:
        await session.commit()
    else:
        await session.rollback()
```

### Selective Import

Import only specific types or groups:

```python
# Filter by type name
types_to_import = ["ГАЛЫН АЮУЛГҮЙ БАЙДАЛ", "ЦАХИЛГААНЫ АЮУЛГҮЙ БАЙДАЛ"]

for type_data in parsed_data.types:
    if type_data.name in types_to_import:
        # Process this type
        pass
```

## Next Steps

After successfully importing questions:

1. **Verify**: Check admin interface or query database
2. **Test**: Create an assessment using imported questions
3. **Deploy**: Commit markdown files to version control
4. **Document**: Update team wiki with new question format

## Additional Resources

- [Data Model](data-model.md) - Entity relationships and validation rules
- [API Contract](contracts/questions-seed-api.md) - Function signatures and behavior
- [Research](research.md) - Technical decisions and tradeoffs
- [Main Spec](spec.md) - Full feature specification

## Support

If you encounter issues not covered in this guide:

1. Check error logs: `tail -f backend/logs/app.log`
2. Review database constraints: Check unique constraints on questions
3. Verify markdown format: Ensure UTF-8 encoding and proper indentation
4. Run tests: `pytest tests/unit/test_questions_seed.py`
