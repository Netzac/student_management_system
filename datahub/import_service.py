import logging
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction, IntegrityError
from django.utils.dateparse import parse_date
from .models import ImportJob, JobLog
from .entity_registry import EntityRegistry
from .io_utils import load_workbook_safe, read_sheet_data, detect_format

logger = logging.getLogger(__name__)

class DataImportService:
    def __init__(self, job_id):
        self.job = ImportJob.objects.get(id=job_id)
        self.entity_config = EntityRegistry.get(self.job.entity_slug)
        self.model = self.entity_config.model
        self.serializer = self.entity_config.serializer_class
        self.stats = {
            'total': 0,
            'success': 0,
            'errors': 0,
            'skipped': 0,
            'duplicates': 0
        }
        self.errors = []

    def _log(self, level, message, row_num=None, raw_data=None):
        """Helper to log to database and console."""
        JobLog.objects.create(
            import_job=self.job,
            row_number=row_num,
            level=level,
            message=message,
            raw_data=raw_data
        )
        if level == 'ERROR':
            logger.error(f"Row {row_num}: {message}")

    def _find_duplicate(self, row_data):
        """
        Tries to find an existing record that might match.
        Default implementation looks for ID or unique fields.
        """
        # Basic logic: if 'id' in row, check by ID
        if 'id' in row_data and row_data['id']:
            try:
                return self.model.objects.get(id=row_data['id'])
            except:
                pass
        return None

    def _transform_row(self, raw_row):
        """
        Override this in specific logic or use serializer directly.
        This maps raw CSV/Excel headers to model fields if needed.
        """
        # Basic pass-through: assuming headers match serializer fields roughly
        return raw_row

    def execute(self):
        self.job.status = 'Processing'
        self.job.save()

        try:
            wb = load_workbook_safe(self.job.file_name)
            headers, rows = read_sheet_data(wb)
            
            self.stats['total'] = len(rows)
            self.job.total_rows = len(rows)
            self.job.save()

            for idx, raw_row in enumerate(rows):
                row_num = idx + 2
                success = self._process_row(raw_row, row_num)
                
                if idx % 50 == 0:
                    # Save checkpoint
                    self.job.imported_rows = self.stats['success']
                    self.job.error_rows = self.stats['errors']
                    self.job.skipped_rows = self.stats['skipped']
                    self.job.duplicate_rows = self.stats['duplicates']
                    self.job.save()

            # Final update
            self.job.status = 'Completed' if self.stats['errors'] == 0 else 'CompletedWithErrors'
            self.job.imported_rows = self.stats['success']
            self.job.error_rows = self.stats['errors']
            self.job.skipped_rows = self.stats['skipped']
            self.job.duplicate_rows = self.stats['duplicates']
            self.job.save()

        except Exception as e:
            logger.exception("Import failed")
            self.job.status = 'Failed'
            self._log('ERROR', f"System Failure: {str(e)}")
            self.job.save()

    def _process_row(self, raw_row, row_num):
        try:
            transformed_data = self._transform_row(raw_row)
            
            # Check for duplicates
            existing = self._find_duplicate(transformed_data)
            
            if existing:
                if self.job.on_duplicate == 'skip':
                    self.stats['duplicates'] += 1
                    self.stats['skipped'] += 1
                    self._log('WARNING', f"Skipped duplicate (ID/Key found)", row_num, raw_row)
                    return False
                elif self.job.on_duplicate == 'overwrite':
                    serializer = self.serializer(instance=existing, data=transformed_data, partial=True)
                else:
                    serializer = self.serializer(data=transformed_data)
            else:
                serializer = self.serializer(data=transformed_data)

            if serializer.is_valid():
                serializer.save()
                self.stats['success'] += 1
                return True
            else:
                self.stats['errors'] += 1
                errors = "; ".join([f"{k}: {v}" for k, v in serializer.errors.items()])
                self._log('ERROR', f"Validation Error: {errors}", row_num, raw_row)
                return False

        except Exception as e:
            self.stats['errors'] += 1
            self._log('ERROR', f"Exception: {str(e)}", row_num, raw_row)
            return False


def run_import_task(job_id):
    """
    Celery Task Entrypoint or direct function call.
    """
    service = DataImportService(job_id)
    service.execute()
