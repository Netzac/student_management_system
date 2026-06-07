# PROJECT MODERNIZATION PROMPT FOR Codex
# Copy everything below this line and paste into Codex

---

# Project: SMS - Modernization Upgrade

## Core Principles
**IMPORTANT**: Whenever you write code, it MUST follow SOLID design principles. Never write code that violates these principles. The upgrade must preserve ALL existing business logic, database schema, and backend functionality. Only UI/UX and frontend technologies may be upgraded.

## Development Workflow
1. **Analyze First**: Run `python manage.py check` and existing tests to understand current state
2. **Create Branch**: Before making changes, create and checkout a feature branch named `feature/modernize-[brief-description]`
3. **Backup Database**: Create a backup of the PostgreSQL database before any migrations
4. **Write Tests**: Write comprehensive tests for all existing functionality to ensure behavior preservation
5. **Incremental Changes**: Make upgrades incrementally, testing after each change
6. **Commit Standards**: Write detailed commit messages explaining the upgrade and confirming no logic changes

## Architecture Overview (Preserve)
- **Backend**: Django (existing version - DO NOT upgrade Django major version unless required)
- **Database**: PostgreSQL (existing schema - DO NOT modify)
- **Business Logic**: All existing views, models, forms, and API endpoints remain unchanged
- **Authentication**: Preserve existing Django auth system

## UPGRADE ALLOWED AREAS (UI/UX Only)
- **Frontend Framework**: Replace Bootstrap with Tailwind CSS (or upgrade Bootstrap to latest v5)
- **JavaScript**: Convert jQuery to vanilla JavaScript or add Alpine.js/HTMX for interactivity
- **CSS**: Replace custom CSS with Tailwind utilities; add responsive design improvements
- **Templating**: Upgrade Django template syntax where beneficial (no logic changes)
- **Form Rendering**: Use django-crispy-forms with Tailwind or Bootstrap 5
- **Icons**: Replace old icon fonts with Lucide or Heroicons
- **Interactivity**: Add smooth transitions, loading states, and micro-interactions
- **Mobile Responsiveness**: Ensure all templates are fully responsive
- **Performance**: Add lazy loading, image optimization, and cache headers

## Code Standards
- **Python**: Follow PEP 8, use type hints for new helper functions only
- **Templates**: Use `{% load static %}` and proper template inheritance
- **Static Files**: Organize in `/static/css/`, `/static/js/`, `/static/images/`
- **CSS**: Use Tailwind CDN or build process (no custom CSS unless absolutely necessary)
- **JavaScript**: Write modular ES6+ code, avoid global variables

## Quality Gates
- **No Logic Changes**: All Django views, models, and forms must work identically
- **Database Integrity**: No schema changes unless absolutely required (document if needed)
- **Test Preservation**: All existing tests must pass; new tests for UI elements optional
- **Browser Compatibility**: Test in modern browsers (Chrome, Firefox, Safari, Edge)
- **Performance**: Lighthouse score must improve or remain above 90 for existing pages

## File Organization (Existing Structure - DO NOT CHANGE)
- **Django Apps**: Keep existing app structure
- **Templates**: `/templates/[app_name]/[template].html` (update content only)
- **Static Files**: `/static/[app_name]/css/`, `/static/[app_name]/js/`
- **Media**: `/media/` (preserve)
- **Management Commands**: Keep all existing commands

## Upgrade Strategy (Follow This Order)

### Phase 1: Assessment & Setup
1. Run `pip freeze` to document current dependencies
2. Run all existing tests: `python manage.py test`
3. Create virtual environment backup
4. Document current UI components and their behavior

### Phase 2: CSS Framework Upgrade
**Option A - Tailwind CSS (Recommended)**
```bash
pip install django-tailwind
python manage.py tailwind init
python manage.py tailwind install
```

**Option B - Bootstrap 5**
```bash
pip install django-bootstrap-v5
# Update settings.py and base template
```

### Phase 3: Template Modernization
- Convert Bootstrap classes to Tailwind (or upgrade to Bootstrap 5)
- Make all templates mobile-first responsive
- Add smooth transitions and hover effects
- Implement dark mode if desired (no logic change)
- Add loading spinners for form submissions

### Phase 4: JavaScript Improvements
- Remove jQuery dependencies where possible
- Add HTMX for dynamic content without writing JS
- OR add Alpine.js for component-like behavior
- Keep all existing form validation and AJAX calls intact

### Phase 5: Performance Optimization
- Add `django-compressor` for static file optimization
- Implement lazy loading for images: `loading="lazy"`
- Add proper cache headers for static files
- Optimize font loading

## Example Template Upgrade

**Before (Bootstrap 3/4):**
```html
<div class="container">
  <form method="post" class="form-horizontal">
    {% csrf_token %}
    <div class="form-group">
      <label class="control-label col-sm-2">Task:</label>
      <div class="col-sm-10">
        <input type="text" class="form-control" name="task">
      </div>
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
  </form>
</div>
```

**After (Tailwind CSS):**
```html
<div class="container mx-auto px-4">
  <form method="post" class="space-y-6">
    {% csrf_token %}
    <div class="space-y-2">
      <label class="block text-sm font-medium text-gray-700">Task:</label>
      <input type="text" name="task" 
             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
    </div>
    <button type="submit" 
            class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
      Submit
    </button>
  </form>
</div>
```

## Prohibited Changes
- ❌ Changing Django model definitions
- ❌ Modifying database schema
- ❌ Altering URL patterns
- ❌ Changing view logic or function signatures
- ❌ Removing or renaming existing templates (only modify content)
- ❌ Changing form validation logic
- ❌ Modifying Django settings except for static files/templates
- ❌ Removing any existing JavaScript functionality
- ❌ Upgrading Django major version (e.g., 2.x → 3.x or 4.x) unless required for security

## Testing Checklist
```bash
# Before any changes
python manage.py test
python manage.py check --deploy

# After each component upgrade
python manage.py test [specific app]
python manage.py runserver

# Final validation
python manage.py test
python manage.py check
```

## Rollback Plan
If any issue occurs:
1. Revert to feature branch
2. Restore database from backup
3. Rollback static files to previous version
4. Document issue for future upgrade attempt

## Success Criteria
- All existing functionality works identically to pre-upgrade version
- UI is modern, responsive, and accessible
- Lighthouse scores improved
- No new bugs introduced
- Development experience improved

## Additional Recommendations for 2020 Django Project
- Add `whitenoise` for static file serving in production
- Implement `django-storages` for CDN integration
- Add `django-debug-toolbar` for development optimization
- Consider adding `django-extensions` for enhanced tooling
- Add `pre-commit` hooks for code quality

---

**Remember**: The goal is a visual and UX upgrade only. The backend Django application should function exactly as before, just looking and feeling modern. Test thoroughly after each change and commit frequently with clear messages.

# END OF PROMPT - COPY EVERYTHING ABOVE THIS LINE