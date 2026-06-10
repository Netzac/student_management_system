from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.text import slugify
from .models import DataProject, ImportJob, ExportJob
from .entity_registry import EntityRegistry
from .import_service import run_import_task
from .export_service import run_export_task

def get_modules_with_entities():
    """Helper to organize entities by module for the dashboard."""
    modules = []
    for mod_name in EntityRegistry.modules():
        modules.append({
            "name": mod_name,
            "entities": EntityRegistry.by_module(mod_name)
        })
    return modules

@login_required
def dashboard(request):
    """Main Data Hub landing page."""
    recent_imports = ImportJob.objects.select_related('imported_by').order_by('-created_at')[:5]
    recent_exports = ExportJob.objects.select_related('exported_by').order_by('-created_at')[:5]
    
    context = {
        "modules": get_modules_with_entities(),
        "recent_imports": recent_imports,
        "recent_exports": recent_exports,
    }
    return render(request, "datahub/dashboard.html", context)

@login_required
def entity_detail(request, entity_slug):
    """View showing import/export options for a single entity."""
    config = EntityRegistry.get(entity_slug)
    
    # Get recent jobs for this entity
    imports = ImportJob.objects.filter(entity_slug=entity_slug).order_by('-created_at')[:5]
    exports = ExportJob.objects.filter(entity_slug=entity_slug).order_by('-created_at')[:5]
    
    context = {
        "config": config,
        "recent_imports": imports,
        "recent_exports": exports,
        "modules": get_modules_with_entities()
    }
    return render(request, "datahub/entity_detail.html", context)

@login_required
def import_start(request, entity_slug):
    """Handles the upload form submission."""
    if request.method == 'POST':
        config = EntityRegistry.get(entity_slug)
        uploaded_file = request.FILES['import_file']
        on_duplicate = request.POST.get('on_duplicate', 'skip')
        
        job = ImportJob.objects.create(
            entity_slug=entity_slug,
            entity_display=config.display_name,
            file_name=uploaded_file,
            file_format='xlsx', # Detected
            imported_by=request.user,
            on_duplicate=on_duplicate,
            status='Queued'
        )
        
        # Run synchronously for now (or use Celery)
        try:
            run_import_task(job.id)
        except Exception as e:
            job.status = 'Failed'
            job.save()
        
        return redirect(reverse('datahub:import_status', kwargs={'job_id': job.id}))
    
    return redirect('datahub:entity_detail', entity_slug=entity_slug)

@login_required
def import_status(request, job_id):
    """Shows results of an import."""
    job = get_object_or_404(ImportJob, id=job_id)
    logs = job.logs.all()
    context = {
        "job": job,
        "logs": logs,
        "modules": get_modules_with_entities()
    }
    return render(request, "datahub/import_status.html", context)

@login_required
def export_start(request, entity_slug):
    """Creates an export job and triggers generation."""
    if request.method == 'POST':
        config = EntityRegistry.get(entity_slug)
        fmt = request.POST.get('format', 'xlsx')
        
        job = ExportJob.objects.create(
            entity_slug=entity_slug,
            entity_display=config.display_name,
            file_format=fmt,
            exported_by=request.user,
            status='Queued'
        )
        
        try:
            run_export_task(job.id)
        except Exception as e:
            job.status = 'Failed'
            job.save()
        
        return redirect(reverse('datahub:export_status', kwargs={'job_id': job.id}))
    return redirect('datahub:entity_detail', entity_slug=entity_slug)

@login_required
def export_status(request, job_id):
    """Shows export status and allows download."""
    job = get_object_or_404(ExportJob, id=job_id)
    context = {
        "job": job,
        "modules": get_modules_with_entities()
    }
    return render(request, "datahub/export_status.html", context)

@login_required
def export_download(request, job_id):
    """Serves the generated file."""
    job = get_object_or_404(ExportJob, id=job_id)
    if not job.output_file:
        return HttpResponse("File not ready.", status=404)
    
    response = HttpResponse(job.output_file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{job.output_file.name}"'
    return response

@login_required
def import_template(request, entity_slug):
    """Generates a blank template file for import."""
    from .io_utils import generate_excel_file
    from .serializers_helpers import safe_str
    
    config = EntityRegistry.get(entity_slug)
    
    # Get headers from serializer
    if config.serializer_class:
        headers = list(config.serializer_class().fields.keys())
    else:
        headers = [f.name for f in config.model._meta.fields]
    
    # Create one row of examples (optional but helpful)
    data = [{}] # Empty template
    # Fill with placeholders
    for h in headers:
        data[0][h] = f"[Example {h}]"
    
    file_obj = generate_excel_file(data, headers)
    
    filename = f"Template_{slugify(config.display_name)}.xlsx"
    response = HttpResponse(file_obj, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
