
### Key Features to Build

2. **Timetable Creator (Main Feature)**
   - Visual drag-and-drop interface for admins
   - Create timetable by: Session → Term → Class → Day
   - Add subject-teacher-room-time combinations
   - Auto-validate for conflicts (teacher double-booking, room clashes, subject repetition)
   - Bulk import from CSV/Excel
   - Save timetable as draft or publish

3. **Conflict Detection**
   - Real-time validation with visual error indicators
   - Conflict types: Teacher availability, Room capacity, Subject frequency limits
   - Automated suggestions for alternative slots

4. **View & Export**
   - Weekly timetable view (by class/day)
   - Teacher timetable view (all classes assigned)
   - Room timetable view (all bookings)
   - Export to PDF/Excel per class, teacher, or room
   - Print-ready layout

5. **User Interface**
   - Dashboard with quick actions
   - Navigation: Sessions → Terms → Classes → Timetables
   - Easy-to-use form wizard for creating timetables
   - Search and filter functionality

---

## 🎨 DESIGN REQUIREMENTS: Microsoft Dynamics 365 Teal Blue Theme

### Color Palette (Dynamics 365 Fluent UI)
```css
/* Primary Colors */
--primary-teal: #00B7C3;        /* Main teal blue */
--primary-dark: #008EA3;        /* Darker teal for hover */
--primary-light: #E0F7F9;       /* Light teal for backgrounds */

/* Secondary Colors */
--accent-blue: #0078D4;         /* Microsoft blue */
--success-green: #107C10;       /* Success states */
--warning-orange: #FFB900;      /* Warnings */
--error-red: #xE81123;          /* Errors/conflicts */

/* Backgrounds & Text */
--bg-white: #FFFFFF;
--bg-light: #F3F2F1;            /* Light gray background */
--bg-dark: #2B2B2B;             /* Dark footer/header */
--text-primary: #201F1E;        /* Primary text */
--text-secondary: #605E5C;      /* Secondary text */
--text-white: #FFFFFF;

/* Borders */
--border-light: #E1DFDD;
--border-medium: #8A8886;
```

### UI Components (Fluent 2 / Dynamics 365 Style)
- **Cards**: White background, subtle shadow (2px), rounded corners (2px)
- **Buttons**: Primary = teal (#00B7C3), Hover = darker teal (#008EA3), rounded (2px)
- **Tables**: Minimal borders, hover rows, teal highlight on selected
- **Forms**: Clean labels, teal focus borders, consistent spacing (8px/16px)
- **Navigation**: Left sidebar or top nav with teal active indicators
- **Icons**: Use Material Icons or Fluent UI Icons
- **Typography**: Segoe UI (Microsoft standard), 14px base, 16px headings
- **Spacing**: 8px grid system, 16px padding on cards

### Django Template Requirements