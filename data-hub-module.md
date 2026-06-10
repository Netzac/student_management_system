**DATA HUB MODULE**

_Implementation Prompt Guide_

Django School Management System

| **For**                 | Trae AI / Claude Code / Cursor / Codex |
| ----------------------- | -------------------------------------- |
| **Convention**          | Microsoft Dynamics 365 Data Management |
| **Architecture Source** | .claude/CLAUDE.md + project inference  |
| **Format**              | 5 Phases - one phase per AI session    |
| **Module**              | datahub/ Django app                    |

_Token budget managed: one phase = one AI session_

# **Overview & Agent Instructions**

⚠ Before starting ANY phase, the agent MUST read CLAUDE.md (and all files under .claude/) and infer the full architecture from the project. Do not assume any model name, app name, URL pattern, auth mixin, or template base - read the project first.

## **What This Document Is**

This document is a phased implementation prompt for adding a Data Hub module to a Django school management system. The module follows Microsoft Dynamics 365 Data Management conventions for import/export. It is split into 5 self-contained phases so that each phase can be completed in a single AI coding session without hitting token limits.

## **Agent Architecture Inference Protocol**

At the start of EVERY phase, the agent must run the following discovery steps before writing a single line of code:

- Read CLAUDE.md in the project root and all files under .claude/ for conventions, naming rules, coding standards, and architectural decisions.
- Run: find . -name 'models.py' | head -30 - list all model files to understand the app structure.
- Run: cat settings.py (or settings/base.py) | grep INSTALLED_APPS - identify all app names.
- Run: grep -r 'class.\*View' --include='\*.py' -l | head -10 - find existing view patterns and auth mixins.
- Run: find templates/ -name 'base.html' -o -name '\*layout\*' | head -5 - identify the base template.
- Run: cat requirements.txt - check which packages are already installed.
- For each entity you are about to serialize, read its model definition first and use exact Python field names.

## **Phase Summary**

| **Phase** | **Title**        | **Scope**                      | **Key Deliverables**                                        |
| --------- | ---------------- | ------------------------------ | ----------------------------------------------------------- |
| 1         | Foundation       | App scaffold, models, registry | datahub/ app, EntityConfig, JobModels, admin, migrations    |
| 2         | Serializers      | All entity serializers         | 12 entity serializers + base class                          |
| 3         | Exporters        | Excel & CSV export engine      | D365-styled workbook exporter, CSV exporter, download views |
| 4         | Importers        | Import engine + validation     | Excel/CSV importer, row validator, duplicate detection      |
| 5         | UI & Integration | Full Data Hub workspace        | Wizard views, workspace tiles, job tracker, error reports   |

## **D365 Conventions - Quick Reference**

These conventions apply to all phases. The agent must never deviate from them.

| **Convention**         | **Rule**                                                                                                             |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Column Headers         | Display Name (Title Case, spaces) - NOT Python field names. e.g. 'First Name \*', not 'first_name'                   |
| Required Fields        | Suffix header with ' \*' (space-asterisk). e.g. 'Last Name \*'                                                       |
| Reserved Columns       | Columns A/B/C of every Excel file: Entity ID \| Status Reason \| Owner - never rename or delete                      |
| Excel Metadata Block   | Rows 1-6 = metadata header (School, Entity, Exported By, Date, Count, blank). Row 7 = column headers. Row 8+ = data. |
| File Naming (export)   | {EntityName}\_{YYYYMMDD}\_{HHMMSS}.xlsx - e.g. Student_Enrollment_20241215_143022.xlsx                               |
| File Naming (template) | {EntityName}\_Template.xlsx - e.g. Guardian_Contact_Template.xlsx                                                    |
| Date Format            | ISO 8601: YYYY-MM-DD in all files                                                                                    |
| CSV Encoding           | UTF-8 with BOM (utf-8-sig) so Excel opens correctly on all locales                                                   |
| Import Sequence        | Unit 1: Reference Data → Unit 2: Master Data → Unit 3: Transactional → Unit 4: Assessment → Unit 5: Finance          |
| Job Status Labels      | Queued → Processing → Completed \| CompletedWithErrors \| Failed                                                     |
| Excel Colors           | Header bg: #0078D4 (MS Blue), Header font: White Bold, Alternating rows: #F3F9FF / White                             |

**PHASE 1** | **Foundation**

_App scaffold · Models · Registry · Admin · Migrations_

ℹ Estimated session scope: ~2,000-3,000 lines of code. Stop after Task 1.5 (migrations run successfully).

## **Session Opening Prompt (paste this to start the session)**

💡 Copy the block below verbatim as your first message to the AI agent.

I am adding a Data Hub module to this Django school management system.

Please start by:

1\. Reading CLAUDE.md and all files under .claude/

2\. Running: find . -name 'models.py' | head -30

3\. Running: cat settings.py | grep -A 30 INSTALLED_APPS

4\. Running: find templates/ -name 'base.html' | head -5

5\. Running: cat requirements.txt

Then implement Phase 1 of the Data Hub module as described below.

## **Task 1.1 - Create the datahub Django App**

Run the following command, then register the app:

python manage.py startapp datahub

Add to INSTALLED_APPS in settings.py (infer the correct settings file path from the project):

"datahub",

⚠ Check if the project uses settings/base.py, settings/local.py, or a single settings.py. Add to the correct file.

## **Task 1.2 - EntityConfig & EntityRegistry (datahub/registry.py)**

Create datahub/registry.py with the following pattern. This is the single source of truth for all entities.

from dataclasses import dataclass, field

from typing import Type

@dataclass

class EntityConfig:

slug: str # e.g. 'student-enrollment'

display_name: str # e.g. 'Student Enrollment'

module: str # e.g. 'Students', 'Finance'

category: str # 'Master Data' | 'Reference Data' | 'Transactional Data'

import_sequence: int # lower = import first

serializer_class: Type # resolved in Phase 2

model: Type # the Django model class

description: str = ''

supports_import: bool = True

supports_export: bool = True

required_fields: list = field(default_factory=list)

class EntityRegistry:

\_registry: dict = {}

@classmethod

def register(cls, config: EntityConfig):

cls.\_registry\[config.slug\] = config

@classmethod

def get(cls, slug: str) -> EntityConfig:

if slug not in cls.\_registry:

raise KeyError(f'Entity not registered: {slug}')

return cls.\_registry\[slug\]

@classmethod

def all(cls) -> list:

return sorted(cls.\_registry.values(), key=lambda e: e.import_sequence)

@classmethod

def by_module(cls, module: str) -> list:

return \[e for e in cls.all() if e.module == module\]

@classmethod

def modules(cls) -> list:

seen = \[\]

for e in cls.all():

if e.module not in seen:

seen.append(e.module)

return seen

ℹ Serializer classes will be None/placeholder in Phase 1. They are wired up in Phase 2 after serializers are written.

## **Task 1.3 - Models (datahub/models.py)**

Create the following three models exactly as specified. Use the AUTH_USER_MODEL from settings, not a hard-coded User import.

### **DataProject**

class DataProject(models.Model):

name = models.CharField(max_length=200)

description = models.TextField(blank=True)

created_by = models.ForeignKey(

settings.AUTH_USER_MODEL,

on_delete=models.SET_NULL, null=True, blank=True,

related_name='data_projects'

)

created_at = models.DateTimeField(auto_now_add=True)

updated_at = models.DateTimeField(auto_now=True)

def \__str_\_(self): return self.name

class Meta: ordering = \['-created_at'\]

### **ImportJob**

class ImportJob(models.Model):

STATUS_CHOICES = \[

('Queued', 'Queued'),

('Processing', 'Processing'),

('Completed', 'Completed'),

('CompletedWithErrors', 'Completed with Errors'),

('Failed', 'Failed'),

\]

project = models.ForeignKey(DataProject, on_delete=models.CASCADE,

related_name='import_jobs', null=True, blank=True)

entity_slug = models.CharField(max_length=100)

entity_display = models.CharField(max_length=200)

file_name = models.CharField(max_length=300)

file_format = models.CharField(max_length=10,

choices=\[('xlsx','Excel'),('csv','CSV')\])

status = models.CharField(max_length=30,

choices=STATUS_CHOICES, default='Queued')

total_rows = models.IntegerField(default=0)

imported_rows = models.IntegerField(default=0)

skipped_rows = models.IntegerField(default=0)

error_rows = models.IntegerField(default=0)

duplicate_rows = models.IntegerField(default=0)

on_duplicate = models.CharField(max_length=10,

choices=\[('skip','Skip'),('overwrite','Overwrite')\],

default='skip')

imported_by = models.ForeignKey(settings.AUTH_USER_MODEL,

on_delete=models.SET_NULL, null=True, related_name='import_jobs')

started_at = models.DateTimeField(null=True, blank=True)

completed_at = models.DateTimeField(null=True, blank=True)

error_file = models.FileField(upload_to='datahub/errors/', null=True, blank=True)

def \__str_\_(self): return f'{self.entity_display} \[{self.status}\]'

class Meta: ordering = \['-started_at'\]

### **ExportJob**

class ExportJob(models.Model):

\# Same STATUS_CHOICES as ImportJob

project = models.ForeignKey(DataProject, on_delete=models.CASCADE,

related_name='export_jobs', null=True, blank=True)

entity_slug = models.CharField(max_length=100)

entity_display = models.CharField(max_length=200)

file_format = models.CharField(max_length=10,

choices=\[('xlsx','Excel'),('csv','CSV')\])

status = models.CharField(max_length=30,

choices=ImportJob.STATUS_CHOICES, default='Queued')

record_count = models.IntegerField(default=0)

filters_applied = models.JSONField(default=dict)

exported_by = models.ForeignKey(settings.AUTH_USER_MODEL,

on_delete=models.SET_NULL, null=True, related_name='export_jobs')

started_at = models.DateTimeField(null=True, blank=True)

completed_at = models.DateTimeField(null=True, blank=True)

output_file = models.FileField(upload_to='datahub/exports/', null=True, blank=True)

def \__str_\_(self): return f'{self.entity_display} \[{self.status}\]'

class Meta: ordering = \['-started_at'\]

### **JobLog**

class JobLog(models.Model):

LEVEL_CHOICES = \[('INFO','Info'),('WARNING','Warning'),('ERROR','Error')\]

import_job = models.ForeignKey(ImportJob, on_delete=models.CASCADE,

related_name='logs', null=True, blank=True)

export_job = models.ForeignKey(ExportJob, on_delete=models.CASCADE,

related_name='logs', null=True, blank=True)

row_number = models.IntegerField(null=True, blank=True)

level = models.CharField(max_length=10, choices=LEVEL_CHOICES)

message = models.TextField()

raw_data = models.JSONField(null=True, blank=True)

created_at = models.DateTimeField(auto_now_add=True)

class Meta: ordering = \['created_at'\]

## **Task 1.4 - App Config (datahub/apps.py)**

ℹ The ready() method will trigger entity registration. In Phase 1, the import will be a stub. Phase 2 fills it in.

class DatahubConfig(AppConfig):

name = 'datahub'

verbose_name = 'Data Hub'

def ready(self):

try:

from datahub import entity_registry # noqa

except ImportError:

pass # entity_registry.py created in Phase 2

## **Task 1.5 - Admin & Migrations**

Register all four models in datahub/admin.py, then create and run migrations.

@admin.register(DataProject)

class DataProjectAdmin(admin.ModelAdmin):

list_display = \['name', 'created_by', 'created_at'\]

search_fields = \['name'\]

@admin.register(ImportJob)

class ImportJobAdmin(admin.ModelAdmin):

list_display = \['entity_display', 'status', 'total_rows',

'imported_rows', 'error_rows', 'imported_by', 'started_at'\]

list_filter = \['status', 'entity_slug', 'file_format'\]

readonly_fields = \['started_at', 'completed_at'\]

@admin.register(ExportJob)

class ExportJobAdmin(admin.ModelAdmin):

list_display = \['entity_display', 'status', 'record_count',

'file_format', 'exported_by', 'started_at'\]

list_filter = \['status', 'entity_slug'\]

@admin.register(JobLog)

class JobLogAdmin(admin.ModelAdmin):

list_display = \['level', 'message', 'row_number', 'created_at'\]

list_filter = \['level'\]

python manage.py makemigrations datahub

python manage.py migrate

💡 Phase 1 is complete when migrations run with no errors and all four models appear in the Django admin.

**PHASE 2** | **Serializers**

_Base serializer · 12 entity serializers · Entity registry wiring_

ℹ Estimated session scope: ~1,500-2,500 lines of code. One serializer per entity. Complete all 12 before closing the session.

## **Session Opening Prompt**

💡 Paste this as the first message of the new session.

Continuing the Data Hub module build - Phase 2: Serializers.

Please start by:

1\. Reading CLAUDE.md and all .claude/ files

2\. For each entity below, read the actual model definition

before writing the serializer. Use exact Python field names.

3\. Run: grep -r 'class Student' --include='\*.py'

(repeat for Teacher, Guardian, Class, Exam, etc.)

Then implement all 12 entity serializers as described below.

## **Task 2.1 - Base Serializer (datahub/serializers/base.py)**

class BaseEntitySerializer:

"""

Maps Django queryset &lt;-&gt; D365-style Display Name dicts.

field_map: {'Display Name Header': 'model_field_or_property'}

"""

field_map: dict = {}

required_fields: list = \[\] # display names of required columns

natural_key_fields: list = \[\] # fields used for duplicate detection

def get_queryset(self):

raise NotImplementedError

def to_export_rows(self, queryset=None) -> list:

qs = queryset if queryset is not None else self.get_queryset()

rows = \[\]

for obj in qs:

row = {}

for display_name, field_name in self.field_map.items():

val = self.\_get_value(obj, field_name)

row\[display_name\] = self.\_format_value(val)

rows.append(row)

return rows

def \_get_value(self, obj, field_name: str):

\# Supports dotted paths: 'guardian.phone_number'

parts = field_name.split('.')

val = obj

for part in parts:

val = getattr(val, part, None)

if val is None: break

return val() if callable(val) else val

def \_format_value(self, val) -> str:

from datetime import date, datetime

if val is None: return ''

if isinstance(val, datetime): return val.strftime('%Y-%m-%d %H:%M')

if isinstance(val, date): return val.strftime('%Y-%m-%d')

return str(val)

def to_import_dict(self, row: dict) -> dict:

reverse_map = {v: k for k, v in self.field_map.items()}

result = {}

for display_name, value in row.items():

field_name = reverse_map.get(display_name)

if field_name:

result\[field_name\] = value

return result

def validate_row(self, row: dict, row_number: int) -> list:

errors = \[\]

for req in self.required_fields:

if not row.get(req, '').strip():

errors.append(f'Row {row_number}: "{req}" is required but empty.')

return errors

def get_example_row(self) -> dict:

return {k: f'Example {k}' for k in self.field_map}

## **Task 2.2 - Entity Serializers**

Create one file per entity under datahub/serializers/. Read the actual model before writing field_map.

⚠ CRITICAL: Before writing each serializer, run grep to find the model and read its fields. Never assume field names.

| **File**            | **Entity**          | **Key field_map entries (Display Name → field path)**                                                                                                                                                                                                    |
| ------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| students.py         | Student Enrollment  | Entity ID→id, First Name \*→first_name, Last Name \*→last_name, Date Of Birth \*→date_of_birth, Gender→gender, Class Name→current_class.name, Enrollment Date→enrollment_date, Status→status, Admission Number→admission_number                          |
| guardians.py        | Guardian Contact    | Entity ID→id, Full Name \*→full_name, Relationship \*→relationship, Phone Number \*→phone_number, Email→email, Student Names→(method: semicolon-join of student names)                                                                                   |
| teachers.py         | Teacher Profile     | Entity ID→id, First Name \*→first_name, Last Name \*→last_name, Email \*→email, Phone Number→phone_number, Department→department.name, Subjects Taught→(method: semicolon-join), Date Joined→date_joined                                                 |
| classes.py          | Class Room          | Entity ID→id, Class Name \*→name, Grade Level \*→grade_level, Academic Year \*→academic_year.label, Class Teacher→teacher.full_name, Capacity→capacity                                                                                                   |
| academic_years.py   | Academic Year       | Entity ID→id, Year Label \*→label, Start Date \*→start_date, End Date \*→end_date, Is Current→is_current                                                                                                                                                 |
| terms.py            | Term                | Entity ID→id, Term Name \*→name, Academic Year \*→academic_year.label, Start Date \*→start_date, End Date \*→end_date                                                                                                                                    |
| subjects.py         | Subject             | Entity ID→id, Subject Name \*→name, Subject Code→code, Department→department.name, Class Name→class_room.name                                                                                                                                            |
| exams.py            | Exam Schedule       | Entity ID→id, Exam Name \*→name, Subject \*→subject.name, Class Name \*→class_room.name, Date \*→exam_date, Start Time→start_time, Duration (mins)→duration_minutes, Max Score→max_score                                                                 |
| results.py          | Student Exam Result | Entity ID→id, Student Full Name \*→student.full_name, Admission Number \*→student.admission_number, Subject \*→exam.subject.name, Exam Name \*→exam.name, Score→score, Grade→grade, Remarks→remarks                                                      |
| attendance.py       | Attendance Record   | Entity ID→id, Student Full Name \*→student.full_name, Class Name \*→class_room.name, Date \*→date, Status \*→status, Remarks→remarks                                                                                                                     |
| fee_structures.py   | Fee Structure       | Entity ID→id, Fee Name \*→name, Class Name \*→class_room.name, Academic Year \*→academic_year.label, Amount \*→amount, Currency→currency, Due Date→due_date                                                                                              |
| fee_transactions.py | Fee Transaction     | Entity ID→id, Student Full Name \*→student.full_name, Admission Number \*→student.admission_number, Fee Name \*→fee_structure.name, Amount Paid \*→amount_paid, Payment Date \*→payment_date, Receipt Number→receipt_number, Balance→outstanding_balance |

## **Task 2.3 - Entity Registry Wiring (datahub/entity_registry.py)**

Create datahub/entity_registry.py - this file imports all serializers and registers all entities. The import sequence numbers follow D365 dependency order.

from datahub.registry import EntityRegistry, EntityConfig

from datahub.serializers.academic_years import AcademicYearSerializer

\# ... import all serializers ...

\# Unit 1 - Reference Data (sequence 100-199)

EntityRegistry.register(EntityConfig(

slug='academic-year', display_name='Academic Year',

module='Academics', category='Reference Data',

import_sequence=100, serializer_class=AcademicYearSerializer,

model=AcademicYear, required_fields=\['Year Label \*', 'Start Date \*', 'End Date \*'\]

))

\# Term: sequence 110, Subject: 120

\# Unit 2 - Master Data (sequence 200-299)

\# ClassRoom: 200, Teacher: 210, Guardian: 220

\# Unit 3 - Students & Enrollment (sequence 300-399)

\# Student Enrollment: 300, Attendance Record: 310

\# Unit 4 - Assessment (sequence 400-499)

\# Exam Schedule: 400, Student Exam Result: 410

\# Unit 5 - Finance (sequence 500-599)

\# Fee Structure: 500, Fee Transaction: 510

💡 Phase 2 is complete when: python manage.py shell -c 'from datahub.registry import EntityRegistry; print(len(EntityRegistry.all()))' prints 12.

**PHASE 3** | **Exporters**

_Excel exporter (D365 theme) · CSV exporter · Download views · URL routing_

ℹ Estimated session scope: ~1,200-2,000 lines of code. The Excel exporter is the most complex piece - it must produce a fully styled, D365-compliant workbook.

## **Session Opening Prompt**

💡 Paste this as the first message of the new session.

Continuing the Data Hub module - Phase 3: Exporters.

Please start by:

1\. Reading CLAUDE.md and all .claude/ files

2\. Checking requirements.txt for openpyxl (add if missing)

3\. Reading datahub/registry.py and datahub/entity_registry.py

to understand the EntityConfig interface

4\. Reading existing views to find the auth mixin and base template

Then implement Phase 3 as described below.

## **Task 3.1 - Dependency Check**

\# Add to requirements.txt if not already present:

openpyxl>=3.1.0

## **Task 3.2 - Excel Exporter (datahub/exporters/excel.py)**

This is the core D365-styled workbook builder. Follow every detail of the specification below.

### **Function signature**

def export_to_excel(

entity_config, # EntityConfig instance

queryset, # Django queryset (already filtered)

exported_by: str, # username string

school_name: str, # from settings.SCHOOL_NAME

template_only=False, # True = blank template, no data rows

) -> BytesIO:

### **Workbook structure (3 sheets)**

| **Sheet** | **Name**            | **Content**                                                                                         |
| --------- | ------------------- | --------------------------------------------------------------------------------------------------- |
| 1         | Data                | Metadata block (rows 1-6) + headers (row 7) + data (row 8+). Or headers only if template_only=True. |
| 2         | Field Reference     | One row per column: Display Name \| Field Type \| Required \| Example Value \| Notes                |
| 3         | Import Instructions | Step-by-step numbered guide for importing this file back                                            |

### **Metadata block (rows 1-6 of Sheet 'Data')**

| **Row** | **Column A**           | **Column B**                                     |
| ------- | ---------------------- | ------------------------------------------------ |
| 1       | School Name            | \[settings.SCHOOL_NAME value\]                   |
| 2       | Entity                 | \[entity_config.display_name\]                   |
| 3       | Exported By            | \[exported_by username\]                         |
| 4       | Export Date            | \[YYYY-MM-DD HH:MM UTC - use datetime.utcnow()\] |
| 5       | Record Count           | \[len(rows)\] or 'Template - no records'         |
| 6       | (blank spacer)         |                                                  |
| 7       | HEADER ROW STARTS HERE |                                                  |

### **D365 color scheme (openpyxl)**

from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

HEADER_FILL = PatternFill('solid', fgColor='0078D4') # MS Blue

HEADER_FONT = Font(name='Calibri', size=11, bold=True, color='FFFFFF')

REQUIRED_FILL = PatternFill('solid', fgColor='FFB900') # Amber for \* marker

ROW_ALT_FILL = PatternFill('solid', fgColor='F3F9FF') # Light blue alt rows

META_LABEL_FONT= Font(name='Calibri', size=10, bold=True, color='605E5C')

META_VALUE_FONT= Font(name='Calibri', size=10, color='1B1B1B')

### **Reserved columns A, B, C (D365 standard)**

\# Column A: 'Entity ID' - pk value on export, blank on template

\# Column B: 'Status Reason' - 'Active'/'Inactive' on export, blank on template

\# Column C: 'Owner' - created_by username on export, blank on template

\# Then: all serializer field_map columns in order

### **Auto-column width + frozen row**

ws.freeze_panes = 'A8' # Freeze rows 1-7 (metadata + header)

for col in ws.columns:

max_len = max(len(str(c.value or '')) for c in col)

ws.column_dimensions\[col\[0\].column_letter\].width = max(15, min(max_len + 4, 60))

⚠ Mark required field headers (those ending with ' \*') with REQUIRED_FILL on the cell background in row 7.

## **Task 3.3 - CSV Exporter (datahub/exporters/csv_exporter.py)**

def export_to_csv(entity_config, queryset, exported_by, school_name) -> str:

"""

Returns CSV string encoded as utf-8-sig (BOM) for Excel compatibility.

No metadata block in CSV - just header row + data.

Headers: same Display Name columns as Excel (Entity ID, Status Reason, Owner, then fields).

All dates: YYYY-MM-DD. All datetimes: YYYY-MM-DD HH:MM.

"""

## **Task 3.4 - File Naming Utility (datahub/utils.py)**

from datetime import datetime

def make_export_filename(display_name: str, fmt: str, template=False) -> str:

"""

D365 naming convention:

Data: Student_Enrollment_20241215_143022.xlsx

Template: Student_Enrollment_Template.xlsx

"""

slug = display_name.replace(' ', '\_')

if template:

return f'{slug}\_Template.{fmt}'

ts = datetime.utcnow().strftime('%Y%m%d\_%H%M%S')

return f'{slug}\_{ts}.{fmt}'

## **Task 3.5 - Export Views (datahub/views.py - export section)**

Add these views to datahub/views.py. Infer the correct staff-only auth mixin from existing project views.

### **ExportWizardView**

GET: Render a 2-step form. Step 1 = entity selector grid. Step 2 = format + filter options + Export/Template buttons.

POST: Call the appropriate exporter, create an ExportJob record, stream the file to the browser.

def post(self, request):

entity_slug = request.POST.get('entity_slug')

file_format = request.POST.get('file_format', 'xlsx')

template_only= 'template' in request.POST

config = EntityRegistry.get(entity_slug)

sz = config.serializer_class()

qs = sz.get_queryset() # apply any filters from POST here

if file_format == 'xlsx':

buf = export_to_excel(config, qs, request.user.username,

settings.SCHOOL_NAME, template_only=template_only)

filename = make_export_filename(config.display_name, 'xlsx', template_only)

response = HttpResponse(buf.getvalue(),

content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

else:

csv_str = export_to_csv(config, qs, request.user.username, settings.SCHOOL_NAME)

filename = make_export_filename(config.display_name, 'csv', template_only)

response = HttpResponse(csv_str.encode('utf-8-sig'), content_type='text/csv; charset=utf-8-sig')

response\['Content-Disposition'\] = f'attachment; filename="{filename}"'

\# Create ExportJob record, return response

### **DownloadTemplateView**

Shortcut GET view: downloads a blank import template for any entity by slug. No form needed.

\# URL: datahub/template/&lt;slug:slug&gt;/?format=xlsx

## **Task 3.6 - URL Configuration (datahub/urls.py - export routes)**

app_name = 'datahub'

urlpatterns = \[

path('export/', ExportWizardView.as_view(), name='export-wizard'),

path('template/&lt;slug:slug&gt;/', DownloadTemplateView.as_view(),name='download-template'),

\]

💡 Phase 3 is complete when: a staff user can download a Student*Enrollment_Template.xlsx and a populated Student_Enrollment*{timestamp}.xlsx, both formatted with the D365 blue header row and 3-sheet structure.

**PHASE 4** | **Importers**

_File parser · Row validator · Duplicate detection · Atomic DB write · Error report_

ℹ Estimated session scope: ~1,500-2,500 lines of code. This phase has the most edge cases - the agent must wrap all DB writes in transactions and never let import failures crash the request.

## **Session Opening Prompt**

💡 Paste this as the first message of the new session.

Continuing the Data Hub module - Phase 4: Importers.

Please start by:

1\. Reading CLAUDE.md and all .claude/ files

2\. Reading datahub/serializers/base.py and one entity serializer

to understand the interface

3\. Reading datahub/models.py for ImportJob and JobLog

4\. Check if Celery is configured: grep -r 'CELERY' settings.py

If yes: make import async. If no: run synchronously.

Then implement Phase 4 as described below.

## **Task 4.1 - Base Importer (datahub/importers/base.py)**

### **parse() - file reader**

def parse(self) -> list:

"""

Returns list of {Display Name: raw_string_value} dicts.

For Excel (.xlsx):

\- Open with openpyxl (read_only=True for memory efficiency)

\- Detect metadata block: if cell A1 value == 'School Name',

skip rows 1-6, treat row 7 as header row.

\- If no metadata block detected, treat row 1 as header.

\- Strip whitespace from all cell values.

\- Convert dates/datetimes to YYYY-MM-DD string.

For CSV (.csv):

\- Detect BOM (utf-8-sig) and strip it.

\- Treat row 1 as header (no metadata block in CSV).

\- Use csv.DictReader.

"""

### **validate() - row-level validation**

def validate(self, rows: list) -> tuple:

"""

Returns (valid_rows, error_rows).

error_rows format: {'\__row_number_\_': N, '\__errors_\_': \['...', '...'\], ...original_row}

Checks per row:

1\. Required fields present and non-empty

2\. Date fields parseable as YYYY-MM-DD

3\. Numeric fields are valid numbers (score, amount, capacity)

4\. Status/choice fields contain allowed values

5\. For each field that is a FK: check if referenced value exists in DB

(e.g. Class Name must match an existing ClassRoom.name)

- log as WARNING (not ERROR) if FK missing; still allow import with null FK

"""

### **detect_duplicates() - before DB write**

def detect_duplicates(self, valid_rows: list) -> tuple:

"""

Returns (unique_rows, duplicate_rows).

Uses serializer.natural_key_fields to check DB for existing records.

Example natural keys:

Student: admission_number

Teacher: email

Guardian: phone_number

ClassRoom: name + academic_year

FeeTransaction: receipt_number

If self.on_duplicate == 'skip': add to duplicate_rows (excluded from import)

If self.on_duplicate == 'overwrite': keep in unique_rows with existing PK

"""

### **import_rows() - atomic DB write**

@transaction.atomic

def import_rows(self, valid_rows: list) -> dict:

"""

Saves records to DB. Returns summary dict.

Per row:

\- Call serializer.to_import_dict(row) to get model field dict

\- If 'Entity ID' is populated: update existing record (Model.objects.filter(pk=id).update(...))

\- If 'Entity ID' is blank: create new record (Model(\*\*kwargs))

\- Catch per-row exceptions with try/except, log to JobLog, continue

\- Wrap the whole loop in savepoint; release on success

After all rows: update ImportJob.status, imported_rows, error_rows, completed_at

"""

## **Task 4.2 - Excel Importer (datahub/importers/excel.py)**

class ExcelImporter(BaseImporter):

def parse(self):

import openpyxl

wb = openpyxl.load_workbook(self.uploaded_file, read_only=True, data_only=True)

ws = wb.active

rows = list(ws.iter_rows(values_only=True))

\# Detect D365 metadata block

if rows and str(rows\[0\]\[0\]).strip() == 'School Name':

header_row_idx = 6 # 0-indexed: row 7 = index 6

else:

header_row_idx = 0

headers = \[str(c).strip() if c else '' for c in rows\[header_row_idx\]\]

data = rows\[header_row_idx + 1:\]

return \[dict(zip(headers, \[str(c).strip() if c else '' for c in r\])) for r in data if any(r)\]

## **Task 4.3 - CSV Importer (datahub/importers/csv_importer.py)**

class CsvImporter(BaseImporter):

def parse(self):

import csv, io

content = self.uploaded_file.read().decode('utf-8-sig')

reader = csv.DictReader(io.StringIO(content))

return \[{k.strip(): v.strip() for k, v in row.items()} for row in reader\]

## **Task 4.4 - Import Error Report Generator**

When an ImportJob completes with errors, generate a downloadable Excel error report.

def generate_error_report(import_job) -> BytesIO:

"""

Reads all JobLog entries with level='ERROR' for this import_job.

Builds an Excel file:

\- Same column structure as the original import file

\- Two appended columns: 'Import Status' | 'Error Details'

\- Error rows: light red background (#FFE6E6)

\- Warning rows: light yellow background (#FFF4CE)

\- Sheet 2: 'Fix Instructions' - how to correct and re-import

File name: Import*Errors*{EntityName}\_{YYYYMMDD}.xlsx

"""

## **Task 4.5 - Import Job View (datahub/views.py - import section)**

### **ImportWizardView - 4 steps**

| **Step**             | **HTTP Method** | **Action**                                                                                                                                                                                              |
| -------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 - Select Entity    | GET             | Render entity selector grid (same as export wizard step 1)                                                                                                                                              |
| 2 - Upload File      | GET/POST        | Form: file upload + duplicate handling radio (Skip / Overwrite). POST saves file, redirects to step 3.                                                                                                  |
| 3 - Validate Preview | GET             | Parse file, run validation. Show first 10 rows in an HTML table. Highlight errors in red. Show column mapping. Show: total rows, valid, errors. 'Confirm Import' button only enabled if valid_rows > 0. |
| 4 - Import           | POST            | Run import_rows(). Create/update ImportJob. Redirect to ImportJobDetailView.                                                                                                                            |

### **ImportJobDetailView**

Shows the full job summary: status badge, stats bar (imported / skipped / errors / duplicates), and a paginated JobLog table. If status is CompletedWithErrors, show a prominent Download Error Report button.

### **JobLogExportView**

\# URL: datahub/jobs/import/&lt;pk&gt;/errors/

\# Calls generate_error_report(job) and streams as attachment

💡 Phase 4 is complete when: uploading a valid Student_Enrollment_Template.xlsx with 5 rows creates 5 Student records, and uploading a file with 2 bad rows produces a downloadable error report.

**PHASE 5** | **UI & Integration**

_Data Hub workspace · All views · URL wiring · Navigation · Settings · Final checks_

ℹ Estimated session scope: ~1,000-2,000 lines of code (mostly templates and URL wiring). This is the finishing phase - the agent assembles everything into a navigable UI.

## **Session Opening Prompt**

💡 Paste this as the first message of the new session.

Continuing the Data Hub module - Phase 5: UI & Integration.

Please start by:

1\. Reading CLAUDE.md and all .claude/ files

2\. Find the base dashboard template:

find templates/ -name '\*.html' | xargs grep -l 'block content' | head -5

3\. Find the CSS framework in use:

grep -r 'bootstrap\\|tailwind\\|bulma' templates/ --include='\*.html' | head -3

4\. Find the existing nav/sidebar to add a Data Hub link:

find templates/ -name '\*nav\*' -o -name '\*sidebar\*' | head -5

5\. Read datahub/registry.py and confirm EntityRegistry.all() returns 12 entities

Then implement Phase 5 as described below.

## **Task 5.1 - Complete URL Configuration (datahub/urls.py)**

app_name = 'datahub'

urlpatterns = \[

path('', DataHubWorkspaceView.as_view(), name='workspace'),

path('projects/', DataProjectListView.as_view(), name='project-list'),

path('projects/new/', DataProjectCreateView.as_view(), name='project-create'),

path('projects/&lt;int:pk&gt;/', DataProjectDetailView.as_view(), name='project-detail'),

path('export/', ExportWizardView.as_view(), name='export-wizard'),

path('template/&lt;slug:slug&gt;/', DownloadTemplateView.as_view(), name='download-template'),

path('import/', ImportWizardView.as_view(), name='import-wizard'),

path('jobs/import/&lt;int:pk&gt;/', ImportJobDetailView.as_view(), name='import-job-detail'),

path('jobs/export/&lt;int:pk&gt;/', ExportJobDetailView.as_view(), name='export-job-detail'),

path('jobs/import/&lt;int:pk&gt;/errors/',JobLogExportView.as_view(), name='job-error-export'),

\]

Include in main project urls.py (infer the correct prefix from existing dashboard URLs):

path('dashboard/datahub/', include('datahub.urls', namespace='datahub')),

## **Task 5.2 - Data Hub Workspace (workspace.html)**

The homepage of the Data Hub. Style it to match the project's existing dashboard aesthetic, but structured like the D365 Data Management workspace.

### **Page layout**

| **Region**        | **Content**                                                                                                             |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Page header       | Title: 'Data Hub' \| Subtitle: 'Import, export, and manage school data' \| Button: 'New Data Project'                   |
| Stat bar          | 4 stat cards: Total Entities (12) \| Import Jobs Today \| Export Jobs Today \| Records Managed                          |
| Entity tiles grid | Cards grouped by module. Each card: icon + entity name + category badge + Export button + Import button + Template link |
| Recent activity   | Table: last 10 jobs (type, entity, status badge, records, user, time). Link to full job history.                        |

### **Entity tile card structure**

{% for module in modules %}

&lt;h3 class='...'&gt; {{ module }} &lt;/h3&gt;

&lt;div class='tile-grid'&gt;

{% for entity in entities_by_module|get:module %}

&lt;div class='tile-card'&gt;

&lt;span class='tile-icon'&gt;...&lt;/span&gt;

&lt;h4&gt;{{ entity.display_name }}&lt;/h4&gt;

&lt;span class='badge'&gt;{{ entity.category }}&lt;/span&gt;

&lt;div class='tile-actions'&gt;

&lt;a href='{% url 'datahub:export-wizard' %}?entity={{ entity.slug }}'&gt;

Export ↓

&lt;/a&gt;

&lt;a href='{% url 'datahub:import-wizard' %}?entity={{ entity.slug }}'&gt;

Import ↑

&lt;/a&gt;

&lt;a href='{% url 'datahub:download-template' entity.slug %}'&gt;

Template

&lt;/a&gt;

&lt;/div&gt;

&lt;/div&gt;

{% endfor %}

&lt;/div&gt;

{% endfor %}

## **Task 5.3 - Settings Updates**

Confirm these settings exist in the project's settings file. Add if missing:

\# Data Hub

SCHOOL_NAME = env('SCHOOL_NAME', default='Our School')

DATAHUB_MAX_IMPORT_ROWS = 10000 # Safety limit per import job

DATAHUB_EXPORT_CHUNK_SIZE = 500 # Queryset chunk size for large exports

\# MEDIA_ROOT must be configured for error file storage

MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = '/media/'

In main urls.py, ensure media files are served in development:

from django.conf import settings

from django.conf.urls.static import static

if settings.DEBUG:

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

## **Task 5.4 - Navigation Integration**

Add a Data Hub link to the project's existing navigation. Infer the nav template location from the project.

⚠ Find the nav file first: find templates/ -name '\*nav\*' -o -name '\*sidebar\*' | head -5. Then add the link inside the staff-only section if one exists.

{% if request.user.is_staff %}

&lt;a href="{% url 'datahub:workspace' %}" class="..."&gt;

Data Hub

&lt;/a&gt;

{% endif %}

## **Task 5.5 - Template Files Checklist**

Create all templates, extending the project's actual base template (discovered in session opening). Use the project's CSS framework.

| **Template**                           | **Key UI Elements**                                                                                        |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| datahub/workspace.html                 | Stat bar, module-grouped entity tile grid, recent jobs table                                               |
| datahub/project_list.html              | Table of DataProjects, New Project button                                                                  |
| datahub/project_detail.html            | Project metadata, Import Jobs table, Export Jobs table                                                     |
| datahub/export_wizard.html             | Entity selector grid (step 1), format + filter form (step 2)                                               |
| datahub/import_wizard.html             | Entity selector (step 1), upload form (step 2), validation preview table (step 3), confirm button (step 4) |
| datahub/job_detail.html                | Status badge, stats row (imported/skipped/errors/dupes), JobLog table, error report download button        |
| datahub/partials/entity_selector.html  | Reusable card grid used by both export and import wizards                                                  |
| datahub/partials/job_status_badge.html | Color-coded badge: Queued=gray, Processing=blue, Completed=green, CompletedWithErrors=amber, Failed=red    |

## **Task 5.6 - Final Integration Checklist**

Run through each of these before declaring Phase 5 complete:

- python manage.py check - no errors
- python manage.py migrate - no pending migrations
- EntityRegistry.all() returns 12 entities
- Staff user can visit /dashboard/datahub/ and see the workspace with all 12 entity tiles
- Download Student Enrollment template → file named Student_Enrollment_Template.xlsx with 3 sheets, D365 blue header, 3 reserved columns
- Export 0 students (empty school) → file with metadata block rows 1-6, header on row 7, no data rows
- Import the template with 3 filled rows → ImportJob created, 3 students created, status = Completed
- Import template with 1 bad row (missing required field) → ImportJob status = CompletedWithErrors, error report downloadable
- All 12 entity Export buttons produce correctly named, correctly formatted files
- Nav link to Data Hub only visible to is_staff users

💡 Phase 5 is complete when all 10 checklist items pass. The Data Hub module is production-ready.

# **Appendix - Quick Reference**

## **A. Import Sequence (D365 Dependency Order)**

| **Unit**       | **Sequence** | **Entity**          | **Depends On**                    |
| -------------- | ------------ | ------------------- | --------------------------------- |
| 1 - Reference  | 100          | Academic Year       | Nothing                           |
| 1 - Reference  | 110          | Term                | Academic Year                     |
| 1 - Reference  | 120          | Subject             | Nothing                           |
| 2 - Master     | 200          | Class Room          | Academic Year, Subject            |
| 2 - Master     | 210          | Teacher Profile     | Nothing                           |
| 2 - Master     | 220          | Guardian Contact    | Nothing                           |
| 3 - Students   | 300          | Student Enrollment  | Class Room, Guardian Contact      |
| 3 - Students   | 310          | Attendance Record   | Student Enrollment, Class Room    |
| 4 - Assessment | 400          | Exam Schedule       | Subject, Class Room               |
| 4 - Assessment | 410          | Student Exam Result | Student Enrollment, Exam Schedule |
| 5 - Finance    | 500          | Fee Structure       | Class Room, Academic Year         |
| 5 - Finance    | 510          | Fee Transaction     | Student Enrollment, Fee Structure |

## **B. File Naming Examples**

| **Scenario**            | **File Name**                                                      |
| ----------------------- | ------------------------------------------------------------------ |
| Export Student data     | Student_Enrollment_20241215_143022.xlsx                            |
| Export Fee Transactions | Fee_Transaction_20241215_143022.csv                                |
| Download blank template | Guardian_Contact_Template.xlsx                                     |
| Error report            | Import_Errors_Student_Enrollment_20241215.xlsx                     |
| Import job upload       | Import_Student_Enrollment_20241215_143022.xlsx (stored internally) |

## **C. D365 Excel Color Reference**

| **Element**           | **Color Code** | **Usage**                                     |
| --------------------- | -------------- | --------------------------------------------- |
| Header background     | #0078D4        | Row 7 (column headers)                        |
| Header font           | #FFFFFF        | White, Bold, Calibri 11pt                     |
| Required field marker | #FFB900        | Cell background for columns ending with ' \*' |
| Alt row fill          | #F3F9FF        | Every other data row                          |
| Error row             | #FFE6E6        | Rows with import errors                       |
| Warning row           | #FFF4CE        | Rows with import warnings                     |
| Metadata label        | #605E5C        | Column A of metadata block                    |

## **D. Token Budget Guide**

Each phase is designed to fit within a typical daily AI coding session. If you hit a token limit mid-phase:

- Save all files written so far and commit them.
- Note the last completed task number.
- Start a new session with: 'Resuming Phase X from Task X.Y. CLAUDE.md and .claude/ files first, then continue from Task X.Y.'
- The agent will re-read the project before continuing - this is intentional and safe.

## **E. Troubleshooting Common Errors**

| **Error**                              | **Fix**                                                                                                               |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| EntityRegistry empty on startup        | Check datahub/apps.py ready() imports entity_registry.py. Check for circular imports.                                 |
| openpyxl not installed                 | pip install openpyxl>=3.1.0 and add to requirements.txt                                                               |
| Excel opens CSV with garbled text      | Ensure CSV is written with utf-8-sig (BOM). Check exporter encoding.                                                  |
| Import skips metadata rows incorrectly | Importer checks if cell A1 == 'School Name'. If metadata block is missing this will fail - verify template structure. |
| Migrations fail: duplicate column      | Check if datahub app was previously partially migrated. Run python manage.py showmigrations datahub.                  |
| is_staff check too restrictive         | Check if project uses a custom permission system. Infer from existing staff-only views in the project.                |
| Template not found                     | Ensure datahub/templates/datahub/ path matches Django's TEMPLATES setting. Check APP_DIRS=True or DIRS.               |