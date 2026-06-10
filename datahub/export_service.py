from django.utils.encoding import smart_str
from .models import ExportJob
from .entity_registry import EntityRegistry
from .io_utils import generate_excel_file, generate_csv_file, normalize_header
from .serializers_helpers import safe_str

class DataExportService:
    def __init__(self, job_id):
        self.job = ExportJob.objects.get(id=job_id)
        self.entity_config = EntityRegistry.get(self.job.entity_slug)
        self.model = self.entity_config.model
        self.serializer = self.entity_config.serializer_class

    def _get_headers(self):
        """Derive headers from serializer fields."""
        if not self.serializer:
            # Fallback to model fields
            return [f.name for f in self.model._meta.fields]
        
        # Use serializer fields as they might have nice names
        return list(self.serializer().fields.keys())

    def execute(self):
        self.job.status = 'Processing'
        self.job.save()

        try:
            # 1. Get Queryset
            qs = self.model.objects.all()
            
            # Apply simple filters if stored (could be expanded)
            # filters = self.job.filters_applied
            # qs = qs.filter(**filters)
            
            count = qs.count()
            self.job.record_count = count
            self.job.save()

            # 2. Prepare Data
            headers = self._get_headers()
            data = []

            # Use serializer to serialize data
            if self.serializer:
                serialized_data = self.serializer(qs, many=True)
                for item in serialized_data.data:
                    # Ensure all headers exist and data is safe for Excel
                    row = {}
                    for h in headers:
                        val = item.get(h, "")
                        row[h] = val
                    data.append(row)
            else:
                # Simple dict fallback
                for obj in qs:
                    row = {}
                    for f in self.model._meta.fields:
                        val = getattr(obj, f.name)
                        row[f.name] = val
                    data.append(row)

            # 3. Generate File
            if self.job.file_format == 'xlsx':
                file_obj = generate_excel_file(data, headers)
            else:
                file_obj = generate_csv_file(data, headers)

            # 4. Save File
            filename = f"export_{self.job.entity_slug}_{self.job.id}.{self.job.file_format}"
            self.job.output_file.save(filename, file_obj)
            
            # 5. Mark as done
            self.job.status = 'Completed'
            self.job.save()

        except Exception as e:
            self.job.status = 'Failed'
            self.job.save()
            raise e

def run_export_task(job_id):
    """
    Task entrypoint.
    """
    service = DataExportService(job_id)
    service.execute()
