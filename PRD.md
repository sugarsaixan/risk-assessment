Got it — **for now Admin is API-only**, and the **Public Form UI** is the only UI to build. Below is the **updated PRD (final for Phase 1)** reflecting that.

---

# PRD — Үнэлгээний Асуулгын Систем (Phase 1: Admin API + Public UI)

## 1) Product Summary

Систем нь байгууллага/хувь хүнээс **нэг удаагийн линкээр** үнэлгээний асуулга бөглүүлж, **төрөл тус бүрийн үнэлгээ** болон **нэгдсэн үнэлгээ**-г бодож хадгална.

**Phase 1 онцлог:**

* Admin UI байхгүй
* Admin тал нь зөвхөн **API**-аар тохируулга/линк үүсгэнэ
* Public тал нь **Монгол кирилл UI**-тай веб форм байна

---

## 2) Users

### 2.1 Admin (API хэрэглэгч)

* Дотоод ажилтан / интеграцийн систем
* Postman / script / internal service ашиглан API дуудна

### 2.2 Respondent (Public)

* Байгууллага эсвэл хувь хүн
* Token линкээр орж бөглөнө (login шаардлагагүй)

---

## 3) In Scope (Phase 1)

### Admin API (required)

* Асуулгын төрөл үүсгэх/засах/идэвхгүй болгох
* Асуулт үүсгэх/засах/идэвхгүй болгох
* YES/NO option rules + score тохируулах
* Respondent үүсгэх/сонгох
* Assessment үүсгэх (төрлүүд сонгоод **one-time link** гаргах)
* Results авах (type score + overall score)

### Public UI (required)

* Token линкээр асуулга нээх
* YES/NO бөглөх
* Conditional: тайлбар/зураг шаардлага хангах
* Submit → үнэлгээ бодогдох → үр дүн харуулах

### Storage

* PostgreSQL (data)
* Image attachments → Object Storage (S3/MinIO/Azure Blob)

---

## 4) Out of Scope (Phase 2+)

* Admin UI
* Multi-language
* AI recommendation
* PDF export / email sending (optional later)

---

## 5) Functional Requirements

### 5.1 Admin API Requirements

**FR-A1** Questionnaire Type CRUD

* scoring_method: SUM (MVP default), optional WEIGHTED, RULES
* thresholds
* weight (overall нэгтгэлд)

**FR-A2** Question CRUD

* type_id, order, (optional weight, critical flag)

**FR-A3** Option settings per YES/NO

* score
* require_comment, require_image
* comment_min_len, max_images, image_max_mb

**FR-A4** Respondent CRUD

* kind: ORG | PERSON, name, optional registration/id

**FR-A5** Create Assessment + One-time Link

* respondent_id
* selected_type_ids[]
* expires_at optional
* snapshot questions/options at creation
* return public_url (token)

**FR-A6** Fetch Assessment Results

* per-type score + overall score
* breakdown optional

---

### 5.2 Public UI Requirements (Mongolian Cyrillic)

**FR-P1** Token access

* `/a/<token>` open form
* show “Нэг удаагийн линк” context and respondent name if available

**FR-P2** Show only selected types’ questions

* grouped by type (optional)
* progress indicator: “8 / 20 асуулт”

**FR-P3** Conditional fields

* If selected option requires comment → show “Тайлбар” (required)
* If selected option requires image → show “Зураг хавсаргах” (required)

**FR-P4** Validation

* Inline errors only, Mongolian Cyrillic messages only
* Must prevent submit if missing required comment/image

**FR-P5** Submit & Results

* On submit:

  * compute type scores + overall score
  * store results
  * show results screen (type + overall)
* link becomes not-submittable after success

**FR-P6** Link status screens

* Expired: “Линкний хугацаа дууссан байна.”
* Used: “Энэ линк аль хэдийн ашиглагдсан байна.”

---

## 6) Scoring Requirements (Phase 1)

### Type Score (SUM)

* raw = Σ(score_awarded)
* max = Σ(max(YESscore, NOscore))
* percent = raw/max * 100
* rating threshold default:

  * ≥80: Бага эрсдэл
  * 50–79: Дунд эрсдэл
  * <50: Өндөр эрсдэл

### Overall Score

* overall_percent = Σ(type_percent * type_weight) / Σ(type_weight)
* overall_rating by thresholds

---

## 7) Security Requirements

* Token stored as **hash** only
* One-time submission enforced
* Rate limit on public endpoints
* Upload restrictions:

  * images only (image/*)
  * size limit (default 5MB)
  * max images per question (default 3)

---

## 8) Non-Functional Requirements

* Mobile-first responsive
* Light/Dark mode
* Load < 2s, submit < 1s (normal cases)
* WCAG AA contrast
* Cyrillic-safe fonts (Inter/Roboto/Noto Sans)

---

## 9) Public API Contract (Minimum Set)

### Admin (protected)

* `POST /admin/types`
* `POST /admin/questions`
* `POST /admin/questions/{id}/options` (YES/NO configs)
* `POST /admin/respondents`
* `POST /admin/assessments` → returns `{ publicUrl }`
* `GET /admin/assessments/{id}/results`

### Public

* `GET /public/a/{token}` → returns assessment snapshot
* `POST /public/a/{token}/upload` → returns attachment key/url
* `POST /public/a/{token}/submit` → returns results

---

## 10) Acceptance Criteria (Phase 1)

* [ ] Admin can fully configure via API and generate one-time link
* [ ] Public UI is Mongolian Cyrillic only + responsive + dark/light
* [ ] Conditional comment/image rules work correctly
* [ ] Type score + overall score computed and stored
* [ ] Used/expired link behavior correct
* [ ] Attachments saved and linked to answers



---
T016
cd backend                                                             
alembic upgrade head 

Phase 2: Foundational is now COMPLETE ✓                                
                                                                         
  To use CLI:                                                            
  cd backend                                                             
  python -m src.cli create-key "My Admin Key"
  python -m src.cli list-keys
                                                                         
  To run backend:                                                        
  cd backend                                                             
  uvicorn src.main:app --reload
                                                                         
  Let me know if you see any errors.



  ---
   /speckit.implement T017 - T024, do not check syntax or install         
  dependencies just give me a instruction todo, i will let you know if   
  there is error. apply this to following tasks 


  ---
T025 - T031
    To run migrations:                                                     
  cd backend                                                             
  alembic upgrade head                                                   
                                                                         
  Let me know if you see any errors.        




  ---- 
Test Key
  GTi1ee9_TxmoGw0h1zexB8aB5UH3_CYiemsw8LI-H5c



    All admin endpoints require authentication via CurrentApiKey dependency
   (X-API-Key header).                                                   
                                                                         
  To test the API:                                                       
  cd backend                                                             
  uvicorn src.main:app --reload                                          
                                                                         
  # Create an API key first                                              
  python -m src.cli create-key "Test Key"                                
                                                                         
  # Then use the key in requests                                         
  curl -H "X-API-Key: dAYc7-fJHBdFR8eLyDj4QDUeygfMx42FLHkdRapZX2w" http://localhost:8000/admin/types
                                                                         
  Let me know if you see any errors.     


API Key created successfully!
ID: bc672920-757f-49df-b211-4b88782a0825
Name: Test Key
Key: dAYc7-fJHBdFR8eLyDj4QDUeygfMx42FLHkdRapZX2w

IMPORTANT: Save this key securely. It cannot be retrieved later.




  ----

  When to Use Each Command
Scenario 	Use This Command	Result
Fresh Database	"alembic upgrade head"	Runs all scripts; creates tables and the version tracking table.
Existing Database	"alembic stamp head"	Does not run scripts; simply tells Alembic the DB is already at the latest version.

--- 


each group has its own result based on sum score of its questions;
   - =IF(F14=0,"Хэвийн",IF(F14=1,"Хянахуйц",IF(F14=2,"Анхаарах",IF(F14=3,"Ноцтой",IF(OR(F14=4,F14=5),"Аюултай",FALSE)))))
each type has its own result 

МАГАДЛАЛЫН ОНОО     - =AVERAGE(GROUP RESULTS)+0.618*STDEV(GROUP RESULTS)
ҮР ДАГАВРЫН ОНОО    - =AVERAGE(each group(=IF(H38="Хэвийн",1,IF(H38="Хянахуйц",2,IF(H38="Анхаарах",3,IF(H38="Ноцтой",4,5))))))+0.618*STDEV(each group(=IF(H38="Хэвийн",1,IF(H38="Хянахуйц",2,IF(H38="Анхаарах",3,IF(H38="Ноцтой",4,5))))))
ЭРСДЭЛ              - МАГАДЛАЛЫН ОНОО * ҮР ДАГАВРЫН ОНОО
ЭРСДЭЛИЙН ЗЭРЭГЛЭЛ  - =IF(H68=1,"AAA",IF(AND(2<=H68,H68<=3),"AA",IF(H68=4,"A",IF(H68=5,"BBB",IF(H68=6,"BB",IF(AND(7<=H68,H68<=9),"B",IF(AND(10<=H68,H68<=11),"CCC",IF(AND(12<=H68,H68<=14),"CC",IF(H68=15,"C",IF(H68=16,"DDD",IF(AND(17<=H68,H68)<=20,"DD","D")))))))))))
ЭРСДЭЛИЙН ТАЙЛБАР   - 
    Зэрэглэл	Тайлбар
    ААА	Эрсдэл маш бага
    АА	Эрсдэл бага
    А	Анхаарахгүй, эрсдэл бага
    BBB	Нийцэхүйц, эрсдэл доогуур
    BB	Авахуйц, эрсдэл доогуур
    B	Хянахуйц, эрсдэл доогуур
    CCC	Хянахуйц, эрсдэл дунд
    CC	Анхаарах, эрсдэл дунд
    C	Нэн анхаарах, эрсдэл дунд
    DDD	Ноцтой, эрсдэл дээгүүр
    DD	Нэн ноцтой, эрсдэл дээгүүр
    D	Аюултай, эрсдэл өндөр


НИЙТ ЭРСДЭЛ = =AVERAGE(each types)+0.618*STDEV(each types)


odoo15

(backend) sugarsaikhan:~/Sources/Projects/Risk-Assessment/backend$ python -m src.cli create-key "Test Key"
2026-02-02 17:17:30,222 INFO sqlalchemy.engine.Engine select pg_catalog.version()
2026-02-02 17:17:30,222 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-02-02 17:17:30,247 INFO sqlalchemy.engine.Engine select current_schema()
2026-02-02 17:17:30,247 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-02-02 17:17:30,253 INFO sqlalchemy.engine.Engine show standard_conforming_strings
2026-02-02 17:17:30,253 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-02-02 17:17:30,256 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-02-02 17:17:30,258 INFO sqlalchemy.engine.Engine INSERT INTO api_keys (key_hash, name, is_active, last_used_at, id) VALUES ($1::VARCHAR, $2::VARCHAR, $3::BOOLEAN, $4::TIMESTAMP WITH TIME ZONE, $5::UUID) RETURNING api_keys.created_at
2026-02-02 17:17:30,258 INFO sqlalchemy.engine.Engine [generated in 0.00012s] ('$argon2id$v=19$m=65536,t=3,p=4$CsE4xzgn5JzTmlMqRaj1Pg$tx7nU+HKXF4qw0cBRMMZgggL5uie12h5i0BS3t108LA', 'Test Key', True, None, UUID('43f22568-0ee1-43cd-b6cf-17e09d9ff354'))
2026-02-02 17:17:30,289 INFO sqlalchemy.engine.Engine COMMIT
API Key created successfully!
ID: 43f22568-0ee1-43cd-b6cf-17e09d9ff354
Name: Test Key
Key: f-_HjKM9Xo_TBNb5H3AuxwoP3FP1l34-j7vYPXkXyEM

IMPORTANT: Save this key securely. It cannot be retrieved later.




------


  🐳 Docker Compose Commands                                                                                                                                                                                                                                            
  
  Step 1: Create Backup                                                                                                                                                                                                                                                 
                                                                                   
  # Using service name (preferred)
  docker compose exec -T postgres pg_dump -U postgres risk_assessment -c -O -x | gzip > /tmp/risk_assessment_backup_$(date +%Y%m%d_%H%M%S).sql.gz

  # Or using container name
  docker exec risk-assessment-db pg_dump -U postgres risk_assessment -c -O -x | gzip > /tmp/risk_assessment_backup_$(date +%Y%m%d_%H%M%S).sql.gz

  Note: The -T flag prevents pg_dump from trying to allocate a TTY, which is needed when piping to gzip.

  Step 2: Clear All Data

  # Using docker compose exec
  docker compose exec postgres psql -U postgres risk_assessment << 'SQL'
  DELETE FROM submission_contacts;
  DELETE FROM assessment_drafts;
  DELETE FROM assessments;
  DELETE FROM respondents;
  DELETE FROM question_options;
  DELETE FROM questions;
  DELETE FROM question_groups;
  DELETE FROM questionnaire_types;
  SQL

  # Or pipe SQL file
  cat << 'SQL' | docker compose exec -T postgres psql -U postgres risk_assessment
  DELETE FROM submission_contacts;
  DELETE FROM assessment_drafts;
  DELETE FROM assessments;
  DELETE FROM respondents;
  DELETE FROM question_options;
  DELETE FROM questions;
  DELETE FROM question_groups;
  DELETE FROM questionnaire_types;
  SQL

  Step 3: Restore from Backup

  # Decompress and restore
  gunzip -c /tmp/risk_assessment_backup_YYYYMMDD_HHMMSS.sql.gz | docker compose exec -T postgres psql -U postgres risk_assessment

  Step 4: Re-seed Questions

  docker compose exec api python -m src.seeds.questions_seed

