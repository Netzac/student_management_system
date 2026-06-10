# Data Hub Module — Django School Management System
## Feature Prompt for Trae AI / Claude Code / Cursor / Codex
## Convention: Microsoft Dynamics 365 Data Management Standards

---

## ROLE & OBJECTIVE

You are implementing a **Data Hub** module for a Django school management system.
This module is the system's central data import/export engine — modelled on Microsoft
Dynamics 365's Data Management workspace conventions. It must be professional,
robust, and production-ready for global school deployments.

Before writing any code, **read the project's CLAUDE.md** (and any `.claude/` slash
command files) in the root of this repository and apply all conventions found there
(naming, formatting, testing, app structure, authentication patterns, etc.).

---

## ARCHITECTURAL OVERVIEW

```
datahub/                    ← new Django app (the "Data Hub" module)
├── __init__.py
├── apps.py
├── models.py               ← DataProject, DataEntity, ImportJob, ExportJob, JobLog
├── registry.py             ← EntityRegistry — central registration of all exportable entities
├── serializers/            ← one serializer per entity (Student, Teacher, Guardian, etc.)
│   ├── __init__.py
│   ├── base.py
│   ├── students.py
│   ├── teachers.py
│   ├── guardians.py
│   ├── classes.py
│   ├── exams.py
│   ├── results.py
│   ├── attendance.py
│   └── fees.py
├── exporters/
│   ├── __init__.py
│   ├── base.py             ← BaseExporter (ABC)
│   ├── excel.py            ← ExcelExporter (openpyxl, D365-styled workbook)
│   └── csv_exporter.py     ← CsvExporter
├── importers/
│   ├── __init__.py
│   ├── base.py             ← BaseImporter (ABC)
│   ├── excel.py            ← ExcelImporter
│   └── csv_importer.py     ← CsvImporter
├── validators.py           ← row-level validation, duplicate detection
├── views.py                ← all CBVs for the Data Hub UI
├── urls.py
├── admin.py
├── tasks.py                ← async Celery tasks (optional, with sync fallback)
├── utils.py                ← helpers: slugify_header, detect_format, stream_response
└── templates/
    └── datahub/
        ├── base.html
        ├── workspace.html          ← Data Hub home (D365-style tile grid)
        ├── project_list.html
        ├── project_detail.html
        ├── export_wizard.html
        ├── import_wizard.html
        ├── job_detail.html
        └── partials/
            ├── entity_selector.html
            ├── field_mapper.html
            └── job_status.html
```

---

## MICROSOFT DYNAMICS 365 CONVENTIONS TO FOLLOW

These conventions must be applied throughout. They are not optional.

### 1. Entity Naming
- Each exportable model is called an **Entity** (not "model" or "table")
- Entity display names match D365 style: `Title Case`, no abbreviations
  - ✅ `Student Enrollment`, `Guardian Contact`, `Fee Transaction`
  - ❌ `student_enroll`, `GuardianContact`, `FeesTxn`

### 2. Column Header Conventions
<cite from D365 Microsoft Learn documentation>
- Column headers = the **Display Name** of the field (not the Python attribute name)
- Headers are Title Case, space-separated words
  - ✅ `First Name`, `Date Of Birth`, `Class Name`, `Guardian Phone Number`
  - ❌ `first_name`, `dob`, `class_name`, `guardian_phone`
- Required fields are marked with an asterisk in the template header row: `First Name *`
- The first three columns of every Excel template are reserved system columns and must
  not be deleted or renamed:
  - Column A: `Entity ID` (internal PK, blank on import for new records)
  - Column B: `Status Reason` (blank on export template, "Active"/"Inactive" on data export)
  - Column C: `Owner` (the user who owns/created the record)

### 3. File Naming Conventions (D365 standard)
- Export files: `{EntityName}_{YYYYMMDD}_{HHMMSS}.xlsx` or `.csv`
  - Example: `Student_Enrollment_20241215_143022.xlsx`
- Template files (blank, for import): `{EntityName}_Template.xlsx`
  - Example: `Guardian_Contact_Template.xlsx`
- Import job files stored as: `Import_{EntityName}_{YYYYMMDD}_{HHMMSS}{ext}`

### 4. Data Project / Job Structure (mirrors D365 Data Management)
- A **Data Project** groups related entities (e.g. "Academic Year Setup 2025")
- Each project has **Jobs**: either Import Jobs or Export Jobs
- Each Job has a **Status**: `Queued → Processing → Completed / CompletedWithErrors / Failed`
- Each Job has a **JobLog** with row-level results

### 5. Import Sequence (D365 dependency order)
Entities must be imported in this order to satisfy foreign key dependencies:
```
Unit 1 (Reference Data):    AcademicYear, Term, Department, Subject
Unit 2 (Master Data):       ClassRoom, Teacher, Guardian
Unit 3 (Transactional):     Student → Enrollment → Attendance
Unit 4 (Assessment):        Exam → ExamResult
Unit 5 (Finance):           FeeStructure → FeePayment
```
This sequence must be enforced in the import wizard UI and documented in templates.

### 6. Excel Workbook Styling (D365 Visual Theme)
The exported Excel files must look professional and follow D365's visual language:
- **Workbook structure**:
  - Sheet 1: `Data` — the actual records
  - Sheet 2: `Field Reference` — one row per column: Display Name, Field Type, Required, Example Value, Notes
  - Sheet 3: `Import Instructions` — step-by-step import guide
- **Color palette** (D365 Fluent theme):
  - Header row background: `#0078D4` (Microsoft Blue)
  - Header row font: White, Bold, 11pt Calibri
  - Required field markers (`*`) in header: `#FFB900` (yellow)
  - Alternating data rows: `#F3F9FF` / White
  - Frozen top row (header always visible)
  - Column widths: auto-fit to content, minimum 15 characters
  - Date columns format: `YYYY-MM-DD` (ISO 8601, universally readable)
  - Number columns: no thousand separator on IDs; 2 decimal places on currency
- **Metadata block** (top-left of Sheet 1, rows 1–5, before the header):
  This is a standard D365 metadata block at the top of every export file:
  ```
  Row 1: School Name        | [value from settings.SCHOOL_NAME]
  Row 2: Entity             | [entity display name]
  Row 3: Exported By        | [username]
  Row 4: Export Date        | [YYYY-MM-DD HH:MM UTC]
  Row 5: Record Count       | [N records]
  Row 6: [blank spacer]
  Row 7: [HEADER ROW starts here]
  Row 8+: [DATA]
  ```
  The importer must skip rows 1–6 and treat row 7 as headers.

---

## ENTITIES TO IMPLEMENT

Implement serializers and register all of the following. Adjust model import paths to
match the actual app structure found in this project (check `settings.INSTALLED_APPS`
and each app's `models.py` before writing import statements).

| Entity Display Name      | Likely App   | Key Fields to Include                                              |
|--------------------------|--------------|---------------------------------------------------------------------|
| Student Enrollment       | students     | ID, First Name *, Last Name *, Date Of Birth *, Gender, Class Name, Enrollment Date, Status |
| Guardian Contact         | students/guardians | ID, Full Name *, Relationship *, Phone Number *, Email, Student IDs (semicolon-separated) |
| Teacher Profile          | teachers/staff | ID, First Name *, Last Name *, Email *, Phone Number, Department, Subjects Taught, Date Joined |
| Class Room               | academics    | ID, Class Name *, Grade Level *, Academic Year *, Class Teacher, Capacity |
| Academic Year            | academics    | ID, Year Label *, Start Date *, End Date *, Is Current |
| Term                     | academics    | ID, Term Name *, Academic Year *, Start Date *, End Date * |
| Subject                  | academics    | ID, Subject Name *, Subject Code, Department, Class Name |
| Exam Schedule            | exams        | ID, Exam Name *, Subject *, Class Name *, Date *, Start Time, Duration (mins), Max Score |
| Student Exam Result      | exams        | ID, Student Full Name *, Admission Number *, Subject *, Exam Name *, Score, Grade, Remarks |
| Attendance Record        | attendance   | ID, Student Full Name *, Class Name *, Date *, Status (Present/Absent/Late/Excused), Remarks |
| Fee Structure            | fees         | ID, Fee Name *, Class Name *, Academic Year *, Amount *, Currency, Due Date |
| Fee Transaction          | fees         | ID, Student Full Name *, Admission Number *, Fee Name *, Amount Paid *, Payment Date *, Receipt Number, Balance |

---

## TASK 1 — Entity Registry (`datahub/registry.py`)

Create a central registry following the D365 entity catalog pattern:

```python
class EntityRegistry:
    """
    Central registry of all exportable/importable entities.
    Mirrors the D365 Data Management entity catalog.
    """
    _registry: dict[str, "EntityConfig"] = {}

    @classmethod
    def register(cls, config: "EntityConfig"):
        cls._registry[config.slug] = config

    @classmethod
    def get(cls, slug: str) -> "EntityConfig":
        ...

    @classmethod
    def all(cls) -> list["EntityConfig"]:
        ...

    @classmethod
    def by_module(cls, module: str) -> list["EntityConfig"]:
        ...


@dataclass
class EntityConfig:
    slug: str               # e.g. "student-enrollment"
    display_name: str       # e.g. "Student Enrollment"
    module: str             # e.g. "Students", "Finance", "Assessment"
    category: str           # "Master Data" | "Reference Data" | "Transactional Data"
    import_sequence: int    # lower = import first (mirrors D365 Unit/Level/Sequence)
    serializer_class: type  # the serializer to use
    model: type             # the Django model
    description: str = ""
    supports_import: bool = True
    supports_export: bool = True
    required_fields: list[str] = field(default_factory=list)
```

Auto-register all entities at app startup in `datahub/apps.py`:
```python
class DatahubConfig(AppConfig):
    name = "datahub"

    def ready(self):
        from datahub import registry  # noqa — triggers all register() calls
```

---

## TASK 2 — Base Serializer (`datahub/serializers/base.py`)

```python
class BaseEntitySerializer:
    """
    Maps a Django queryset → list of dicts with D365-style Display Name keys.
    Also maps import rows (Display Name keys) → validated model field dicts.
    """
    # Subclasses define this: {"Display Name Header": "model_field_or_property"}
    field_map: dict[str, str] = {}
    required_fields: list[str] = []   # display names of required columns

    def get_queryset(self) -> QuerySet:
        raise NotImplementedError

    def to_export_rows(self, queryset=None) -> list[dict]:
        """Convert queryset to list of {Display Name: value} dicts."""

    def to_import_dict(self, row: dict) -> dict:
        """Convert {Display Name: value} import row to {model_field: value} dict."""

    def validate_row(self, row: dict, row_number: int) -> list[str]:
        """Return list of validation error strings for a single row."""

    def get_example_row(self) -> dict:
        """Return one example row for the Field Reference sheet."""
```

---

## TASK 3 — Excel Exporter (`datahub/exporters/excel.py`)

Requirements (strictly follow the D365 workbook structure above):

- Use `openpyxl` (add to requirements.txt if not present)
- Build the workbook in memory, return as `BytesIO`
- Apply the full D365 visual theme (colors, fonts, frozen rows, auto-width)
- Include all 3 sheets: `Data`, `Field Reference`, `Import Instructions`
- Write the metadata block (rows 1–6) before the header row
- Mark required field headers with `*` suffix and yellow fill on the asterisk cell
- Function signature:
  ```python
  def export_to_excel(
      entity_config: EntityConfig,
      queryset,
      exported_by: str,
      school_name: str,
  ) -> BytesIO:
  ```
- File should be downloadable with the correct D365-style filename

---

## TASK 4 — CSV Exporter (`datahub/exporters/csv_exporter.py`)

- Headers = Display Name columns (same as Excel)
- UTF-8 with BOM (`utf-8-sig`) — required for Microsoft Excel to open correctly on all locales
- ISO 8601 dates (`YYYY-MM-DD`)
- Function:
  ```python
  def export_to_csv(entity_config, queryset, exported_by, school_name) -> str:
  ```
- Returns the CSV as a string (caller wraps in `StreamingHttpResponse`)

---

## TASK 5 — Excel & CSV Importers

### `datahub/importers/base.py`

```python
class BaseImporter:
    def __init__(self, entity_config: EntityConfig, uploaded_file, imported_by):
        ...

    def parse(self) -> list[dict]:
        """
        Parse the file into list of {Display Name: raw_value} dicts.
        For Excel: skip metadata rows 1–6, treat row 7 as header.
        For CSV: treat row 1 as header (no metadata block in CSV imports).
        Strip whitespace from all values.
        """

    def validate(self, rows: list[dict]) -> tuple[list[dict], list[dict]]:
        """
        Returns (valid_rows, error_rows).
        error_rows include {"__row_number__": N, "__errors__": ["...", "..."]}
        Check: required fields present, data types valid, foreign keys resolvable.
        """

    def import_rows(self, valid_rows: list[dict]) -> ImportJobResult:
        """
        Bulk-create or update records.
        If Entity ID column is populated → update existing record.
        If Entity ID is blank → create new record.
        Use Django's bulk_create with update_conflicts where supported.
        Wrap entire operation in a database transaction.
        """
```

### Duplicate detection
- Before saving, check if a record with the same natural key already exists
  (e.g. for Student: Admission Number; for Teacher: Email; for Class: Name + Year)
- On duplicate: default behavior = **Skip** (log warning); user can choose **Overwrite**
- Show duplicate count in the job summary

---

## TASK 6 — Job & Log Models (`datahub/models.py`)

```python
class DataProject(models.Model):
    """Mirrors D365 Data Management > Data Projects."""
    name           = models.CharField(max_length=200)
    description    = models.TextField(blank=True)
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)


class ImportJob(models.Model):
    STATUS_CHOICES = [
        ("Queued",               "Queued"),
        ("Processing",           "Processing"),
        ("Completed",            "Completed"),
        ("CompletedWithErrors",  "Completed with Errors"),
        ("Failed",               "Failed"),
    ]
    project        = models.ForeignKey(DataProject, on_delete=models.CASCADE, related_name="import_jobs", null=True, blank=True)
    entity_slug    = models.CharField(max_length=100)    # references EntityRegistry
    entity_display = models.CharField(max_length=200)
    file_name      = models.CharField(max_length=300)
    file_format    = models.CharField(max_length=10, choices=[("xlsx","Excel"),("csv","CSV")])
    status         = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Queued")
    total_rows     = models.IntegerField(default=0)
    imported_rows  = models.IntegerField(default=0)
    skipped_rows   = models.IntegerField(default=0)
    error_rows     = models.IntegerField(default=0)
    duplicate_rows = models.IntegerField(default=0)
    on_duplicate   = models.CharField(max_length=10, choices=[("skip","Skip"),("overwrite","Overwrite")], default="skip")
    imported_by    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    started_at     = models.DateTimeField(null=True)
    completed_at   = models.DateTimeField(null=True)
    error_file     = models.FileField(upload_to="datahub/errors/", null=True, blank=True)  # downloadable error report


class ExportJob(models.Model):
    STATUS_CHOICES = ImportJob.STATUS_CHOICES
    project        = models.ForeignKey(DataProject, on_delete=models.CASCADE, related_name="export_jobs", null=True, blank=True)
    entity_slug    = models.CharField(max_length=100)
    entity_display = models.CharField(max_length=200)
    file_format    = models.CharField(max_length=10, choices=[("xlsx","Excel"),("csv","CSV")])
    status         = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Queued")
    record_count   = models.IntegerField(default=0)
    filters_applied = models.JSONField(default=dict)    # which filters were applied on export
    exported_by    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    started_at     = models.DateTimeField(null=True)
    completed_at   = models.DateTimeField(null=True)
    output_file    = models.FileField(upload_to="datahub/exports/", null=True, blank=True)


class JobLog(models.Model):
    """Row-level log entry. One record per processed row."""
    LEVEL_CHOICES = [("INFO","Info"),("WARNING","Warning"),("ERROR","Error")]
    import_job   = models.ForeignKey(ImportJob, on_delete=models.CASCADE, related_name="logs", null=True, blank=True)
    export_job   = models.ForeignKey(ExportJob, on_delete=models.CASCADE, related_name="logs", null=True, blank=True)
    row_number   = models.IntegerField(null=True)
    level        = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message      = models.TextField()
    raw_data     = models.JSONField(null=True, blank=True)   # the original row dict
    created_at   = models.DateTimeField(auto_now_add=True)
```

---

## TASK 7 — Views (`datahub/views.py`)

All views require `is_staff=True`. Use `UserPassesTestMixin` or a custom mixin
already used in this project (check existing views before creating a new one).

### View list

| View Class               | URL                             | Description |
|--------------------------|---------------------------------|-------------|
| `DataHubWorkspaceView`   | `datahub/`                      | Home — D365-style tile grid of all entities grouped by module |
| `DataProjectListView`    | `datahub/projects/`             | List of all Data Projects |
| `DataProjectCreateView`  | `datahub/projects/new/`         | Create a new Data Project |
| `DataProjectDetailView`  | `datahub/projects/<pk>/`        | Project detail: list of import/export jobs |
| `ExportWizardView`       | `datahub/export/`               | Step 1: select entity. Step 2: select format + filters. Step 3: download |
| `DownloadTemplateView`   | `datahub/template/<slug>/`      | Instantly download blank import template for any entity |
| `ImportWizardView`       | `datahub/import/`               | Step 1: select entity. Step 2: upload file. Step 3: validate preview. Step 4: confirm |
| `ImportJobDetailView`    | `datahub/jobs/import/<pk>/`     | Job detail with progress, stats, and row-level log |
| `ExportJobDetailView`    | `datahub/jobs/export/<pk>/`     | Job detail with download link |
| `JobLogExportView`       | `datahub/jobs/import/<pk>/errors/` | Download error rows as Excel for correction and re-import |

### Export Wizard detail (ExportWizardView)
- **Step 1**: Entity selector — card grid, grouped by module (Students / Finance / Assessment / etc.)
- **Step 2**: Filter options (date range, class, academic year, status) + format choice (Excel / CSV)
  - "Export Data" button → export with data
  - "Download Template" button → export blank template with headers only
- **Step 3**: File auto-downloads; job record created; summary shown

### Import Wizard detail (ImportWizardView)
- **Step 1**: Entity selector (same card grid as export)
- **Step 2**: Upload `.xlsx` or `.csv` file; duplicate handling option (Skip / Overwrite)
- **Step 3**: **Validation Preview** — show first 10 rows parsed, highlight errors in red, show column mapping table. User must explicitly confirm before any DB writes.
- **Step 4**: Import runs; redirect to `ImportJobDetailView` for live status.

---

## TASK 8 — Data Hub Workspace UI (`workspace.html`)

The home page must visually resemble the D365 Data Management workspace:

- Page title: **"Data Hub"** with subtitle: *"Import, export, and manage school data"*
- **Tile grid** — one card per entity, grouped by module section:
  ```
  [Module heading: "Students"]
    [Student Enrollment tile]  [Guardian Contact tile]  [Attendance Record tile]
  [Module heading: "Staff"]
    [Teacher Profile tile]
  [Module heading: "Academics"]
    [Class Room tile]  [Subject tile]  [Academic Year tile]  [Term tile]
  [Module heading: "Assessment"]
    [Exam Schedule tile]  [Student Exam Result tile]
  [Module heading: "Finance"]
    [Fee Structure tile]  [Fee Transaction tile]
  ```
- Each tile shows:
  - Entity icon (use a Fluent/Bootstrap icon appropriate to entity type)
  - Entity display name
  - Category badge: `Master Data` / `Reference Data` / `Transactional Data`
  - Two action buttons: **Export ↓** and **Import ↑**
- Sidebar or top section: **Recent Jobs** — last 5 import/export jobs with status badges
- Top-right: **"New Data Project"** button

---

## TASK 9 — Import Error Report

When an import completes with errors (`CompletedWithErrors`):
- Generate a downloadable Excel error report at `ImportJobDetailView`
- The error report is the original file rows that failed, with two new columns appended:
  - Column: `Import Status` (value: `Error`)
  - Column: `Error Details` (pipe-separated list of validation messages)
- Row background: `#FFF4CE` (light yellow) for warnings, `#FFE6E6` (light red) for errors
- File name: `Import_Errors_{EntityName}_{YYYYMMDD}.xlsx`
- Instructions sheet included: "Fix the highlighted rows and re-import this file"

---

## TASK 10 — URL Configuration

`datahub/urls.py`:
```python
app_name = "datahub"

urlpatterns = [
    path("",                          DataHubWorkspaceView.as_view(),  name="workspace"),
    path("projects/",                 DataProjectListView.as_view(),   name="project-list"),
    path("projects/new/",             DataProjectCreateView.as_view(), name="project-create"),
    path("projects/<int:pk>/",        DataProjectDetailView.as_view(), name="project-detail"),
    path("export/",                   ExportWizardView.as_view(),      name="export-wizard"),
    path("template/<slug:slug>/",     DownloadTemplateView.as_view(),  name="download-template"),
    path("import/",                   ImportWizardView.as_view(),      name="import-wizard"),
    path("jobs/import/<int:pk>/",     ImportJobDetailView.as_view(),   name="import-job-detail"),
    path("jobs/export/<int:pk>/",     ExportJobDetailView.as_view(),   name="export-job-detail"),
    path("jobs/import/<int:pk>/errors/", JobLogExportView.as_view(),  name="job-error-export"),
]
```

Include in project `urls.py`:
```python
path("dashboard/datahub/", include("datahub.urls", namespace="datahub")),
```

---

## TASK 11 — Migrations & Dependencies

New pip dependencies (add to `requirements.txt`):
```
openpyxl>=3.1.0         # Excel read/write
```

Migration:
```bash
python manage.py makemigrations datahub
python manage.py migrate
```

---

## TASK 12 — Admin Registration

```python
# datahub/admin.py
@admin.register(DataProject)
class DataProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "created_at"]

@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ["entity_display", "status", "total_rows", "imported_rows", "error_rows", "imported_by", "started_at"]
    list_filter  = ["status", "entity_slug", "file_format"]
    readonly_fields = ["started_at", "completed_at", "total_rows", "imported_rows", "error_rows"]

@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ["entity_display", "status", "record_count", "file_format", "exported_by", "started_at"]
    list_filter  = ["status", "entity_slug", "file_format"]
```

---

## IMPORTANT CONSTRAINTS

1. **Read CLAUDE.md first.** Apply all project conventions before writing any code.
2. **Never hard-code model import paths.** Check the actual app structure first with
   `find . -name "models.py" | xargs grep -l "class Student"` (or equivalent).
3. **Never assume field names.** Before writing any serializer, read the model's
   actual field definitions and use the exact Python attribute names in `field_map`.
4. **Django transactions.** Wrap all import DB writes in `transaction.atomic()`.
   If any row causes an unhandled exception, roll back only that row, not the whole job.
5. **No file storage required for export.** Small exports (<10,000 rows) stream directly
   to the browser. Only store the file in `ExportJob.output_file` if Celery is available.
6. **UTF-8 with BOM for CSV.** Always use `utf-8-sig` encoding so Excel opens correctly.
7. **Date format: ISO 8601.** All dates exported as `YYYY-MM-DD`. All times as `HH:MM UTC`.
8. **The metadata block in Excel must be skipped on import.** The importer reads row 7
   as the header row (rows 1–6 = metadata, row 6 = blank spacer).
9. **D365 file naming convention is mandatory.** All generated files must follow the
   naming rules in the Conventions section above.
10. **The entity registry must be the single source of truth.** The UI, exporters,
    importers, and admin should all derive entity information from `EntityRegistry`,
    never from hard-coded lists.

---

## PRE-IMPLEMENTATION CHECKLIST FOR THE AI TOOL

Before writing any code, answer these by reading the project:

1. What is the base template that all admin/dashboard templates extend?
   (Check `templates/` for a `base.html` or dashboard layout)
2. What authentication mixin does this project use for staff-only views?
   (Check existing views — `LoginRequiredMixin`? Custom `StaffRequiredMixin`?)
3. What CSS framework is used? (Bootstrap 5? Tailwind? Custom?)
4. Does `settings.py` already define `SCHOOL_NAME`? If not, add it.
5. What are the actual app names in `INSTALLED_APPS` for students, teachers, fees, exams?
6. Does the project already use `openpyxl`? (Check `requirements.txt`)
7. Is Celery configured? If yes, make import jobs async. If no, run synchronously.
8. What is the `MEDIA_ROOT` / `MEDIA_URL` configuration for file storage?

---

*End of prompt. Implement tasks in order 1 → 12.
Confirm answers to the Pre-Implementation Checklist before writing the first line of code.*
