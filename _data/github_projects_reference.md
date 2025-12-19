# GitHub Projects MCP Reference

## Overview
Claude has access to GitHub Projects V2 via the `github-projects` MCP server (Arclio).
This document captures working capabilities, known limitations, and UI navigation guidance.

---

## Working Operations ✅

### List & Read
- `list_projects` — List all projects for a user/org
- `get_project_fields` — Get field IDs and single-select option IDs
- `get_project_items` — List items in a project (supports filtering, pagination)

### Create
- `create_issue` — Create issue in a repository
- `create_draft_issue` — Create draft issue directly in project
- `add_issue_to_project` — Add existing issue to a project

### Update
- `update_project_item_field` — Update field values on project items
  - ✅ Works for: Single-select fields (Status, custom single-selects like Phase)
  - ❌ Fails for: Date fields, Milestone field (mirrored from repo)

### Delete
- `delete_project_item` — Remove item from project

---

## Known Limitations ❌

### Cannot Create via API
- Custom fields (must create manually in Project Settings)
- Views (Board, Table, Roadmap — must create manually)
- Repository milestones
- Labels

### Cannot Update via API
- **Date fields** — API returns generic error, no specific reason
- **Milestone field** — This is a mirrored field from the repository; must be set on the issue itself via Issues API (not available in this MCP)
- **Labels** — Same as Milestone, repo-level property

### View Configuration
- Cannot set which fields a view displays
- Cannot set grouping or sorting
- Cannot configure Roadmap date field mappings

---

## Field Types Reference

| Field Type | Can Read | Can Write | Notes |
|------------|----------|-----------|-------|
| Title | ✅ | ✅ | |
| Status | ✅ | ✅ | Use option ID, not name |
| Single Select (custom) | ✅ | ✅ | Use option ID, not name |
| Date | ✅ | ❌ | API silently fails |
| Milestone | ✅ | ❌ | Mirrored from repo |
| Labels | ✅ | ❌ | Mirrored from repo |
| Assignees | ✅ | ❌ | Mirrored from repo |
| Text | ✅ | ✅ | |
| Number | ✅ | ✅ | |
| Iteration | ✅ | ? | Untested |

---

## UI Navigation Guide

When API limitations require manual intervention, use these exact click-paths.

### Repository vs Project Properties

| Attribute Type | Examples | Managed At | API Access |
|----------------|----------|------------|------------|
| **Issue Properties** | Labels, Milestones, Assignees | Repository Level | ❌ Requires Repo API |
| **Project Properties** | Status, Custom Fields (Phase) | Project Level | ✅ Full Read/Write |
| **Draft Issues** | Ideas not yet converted | Project Level | ✅ Full Read/Write |

### Accessing Project Settings

1. Open the project in browser
2. Locate the **three-dot menu (`...`)** in the top-right corner (next to "Insights")
3. Select **⚙️ Settings**

### Creating Custom Fields

1. Navigate to **Project Settings** (three-dot menu → Settings)
2. Click **Fields** in the left sidebar
3. Click **+ New field** button
4. Configure:
   - **Field name:** e.g., "Start Date"
   - **Field type:** Select from dropdown (Text, Number, Date, Single select, Iteration)
5. Click **Save**

### Creating Views

1. Locate tabs at top of project (e.g., "View 1")
2. Click **+ New view** at the end of tabs
3. Select layout: **Table**, **Board**, or **Roadmap**
4. To rename: Double-click tab name or click dropdown arrow `⌄` → **Rename**

---

## Roadmap View Configuration

### Mapping Date Fields (Critical Step)

If items aren't appearing on timeline, the date field mapping is likely unset.

1. In Roadmap view, look at the **top-right toolbar**
2. Click the **🗓️ Date fields** button
3. Use dropdowns to map:
   - **Start date:** Select your "Start Date" field
   - **Target date:** Select your "Target Date" field
4. Items with dates populated will now appear as bars on the timeline

### Adding Dates to Items

Since API cannot set Date fields, use these methods:

- **Table View (Recommended):** Switch to Table view, click date cell, use calendar picker
- **Drag-and-Drop:** Drag item from "No dates" sidebar onto timeline grid
- **Timeline Expansion:** Hover over bar edge, drag handle to extend duration

### Roadmap Troubleshooting

| Problem | Solution |
|---------|----------|
| Items not appearing | Ensure item has values in BOTH Start and Target date fields |
| Clicking does nothing | Check if view is "Grouped" with collapsed rows — click `>` to expand |
| Timeline empty | Click "Date fields" button and map your custom date fields |
| Filters hiding items | Check search bar for active filters |

---

## View Configuration Reference

### Table View

- **Adding Columns:** Click **+** at far right of table headers, select field
- **Grouping:** Click **Group** button → select field (creates swimlanes)
- **Sorting:** Click **Sort** button → choose field and direction
- **Bulk Edit:** Check multiple items → floating bar appears at bottom → apply field value to all

### Board View

- **Column Field:** Click **Column field** button to change what columns represent
- **Moving Items:** Drag cards horizontally to update field value
- **WIP Limits:** Click `...` at top of column → Set a limit

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Open Command Palette |
| `Arrow Keys` | Navigate cells in Table view |
| `Enter` | Edit selected cell |

---

## Troubleshooting Guidance Templates

When encountering errors, provide these specific instructions:

**Cannot set date field:**
> "I'm unable to set dates via the API. Please open Table view, find the [Date Field] column, and select the date manually using the calendar picker."

**Milestone not found:**
> "Milestones are managed at the Repository level, not Project level. Go to Repository → Issues → Milestones to create it, then assign issues to it from there."

**Roadmap is empty:**
> "Please click the 'Date fields' button in the top-right of Roadmap view and ensure 'Start Date' and 'Target Date' are mapped to your custom fields."

---

## Roadmap Setup Checklist

When user asks to "set up a roadmap":

1. **Check Fields Exist:**
   - Do "Start Date" and "Target Date" fields exist?
   - If not → Guide to Settings → Fields → + New field

2. **Check Data Populated:**
   - Do items have dates?
   - If not → Guide to Table View to enter dates

3. **Check Mapping Configured:**
   - Is Roadmap looking at correct fields?
   - If not → Guide to 🗓️ Date fields button

---

## Workflow: Populating a Project

### What Claude Can Do Autonomously
1. Create issues with titles and descriptions
2. Add issues to projects
3. Assign custom single-select fields (Phase, Priority, etc.)
4. Update Status (Todo → In Progress → Done)
5. Delete items from project

### What Requires Manual Setup (One-Time)
1. Create custom fields in Project Settings
2. Create views (Board, Table, Roadmap)
3. Configure Roadmap date field mappings
4. Set dates on items (via Table view or dragging in Roadmap)

### Recommended Setup for EhkoForge
1. **Brent creates once:**
   - Phase field (single-select): MVP Core, Ingot Pipeline, Website, Voice & Context, Infrastructure
   - Start Date field (date)
   - Target Date field (date)
   - Board view (by Status)
   - Table view (for bulk editing)
   - Roadmap view (mapped to Start Date / Target Date)

2. **Claude manages ongoing:**
   - Creating new issues
   - Phase assignments
   - Status updates
   - Item descriptions

3. **Brent manages ongoing:**
   - Setting/adjusting dates (drag in Roadmap or edit in Table view)

---

## Key IDs for EhkoForge Roadmap (Project #3)

### Field IDs
```
Status: PVTSSF_lAHOAM-dWs4BK6kmzg6pPmo
Phase: PVTSSF_lAHOAM-dWs4BK6kmzg6pamg
Start Date: PVTF_lAHOAM-dWs4BK6kmzg6paog
Target Date: PVTF_lAHOAM-dWs4BK6kmzg6pao8
```

### Status Options
```
Todo: f75ad846
In Progress: 47fc9ee4
Done: 98236657
```

### Phase Options
```
MVP Core: 46b16352
Ingot Pipeline: 13c3557d
Website: 672e9cd2
Voice & Context: f4f73e23
Infrastructure: db917a88
```

---

## Example Commands

### Update Status to "In Progress"
```
update_project_item_field(
  owner="brentyJ",
  project_number=3,
  item_id="PVTI_xxx",
  field_id="PVTSSF_lAHOAM-dWs4BK6kmzg6pPmo",
  field_value="47fc9ee4"
)
```

### Update Phase to "Website"
```
update_project_item_field(
  owner="brentyJ",
  project_number=3,
  item_id="PVTI_xxx",
  field_id="PVTSSF_lAHOAM-dWs4BK6kmzg6pamg",
  field_value="672e9cd2"
)
```

---

**Changelog**
- v1.1 — 2025-12-19 — Added UI Navigation Guide, Roadmap configuration, troubleshooting templates (merged from Gemini research)
- v1.0 — 2025-12-19 — Initial documentation based on Session 42 testing
