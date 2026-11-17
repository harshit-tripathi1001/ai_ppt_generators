# Entity Relationship Diagram

> **Note**: The AI PPT Generator uses no relational database. All data is held
> in-memory via Pydantic models during a single session. The following ER diagram
> represents the **logical data model** derived from the Pydantic schema in
> `src/content_schema.py`.

## Figure 13 — Logical Data Model (Pydantic Schema as ER)

```mermaid
erDiagram
    PRESENTATION_DATA {
        string title
        string subtitle
        string theme
        string font_family
        int    font_size
        string aspect_ratio
        bool   include_speaker_notes
    }

    SLIDE_CONTENT {
        string layout
        string title
        string body_text
        string speaker_notes
    }

    BULLET {
        string text
        int    order
    }

    KPI_METRIC {
        string label
        string value
        string trend
        string description
    }

    COLUMN_DATA {
        string left_title
        string right_title
    }

    COLUMN_BULLET {
        string text
        string side
        int    order
    }

    TABLE_DATA {
        string caption
    }

    TABLE_HEADER {
        string text
        int    col_index
    }

    TABLE_ROW {
        int row_index
    }

    TABLE_CELL {
        string text
        int    col_index
    }

    CHART_DATA {
        string chart_type
        string title
        string x_axis_label
        string y_axis_label
    }

    CHART_SERIES {
        string name
    }

    CHART_VALUE {
        string category
        float  value
    }

    PROCESS_STEP {
        string step_number
        string title
        string description
        string icon
    }

    PRESENTATION_DATA ||--o{ SLIDE_CONTENT : "contains"
    SLIDE_CONTENT ||--o{ BULLET : "has"
    SLIDE_CONTENT ||--o| KPI_METRIC : "may have"
    SLIDE_CONTENT ||--o| COLUMN_DATA : "may have"
    COLUMN_DATA ||--o{ COLUMN_BULLET : "has"
    SLIDE_CONTENT ||--o| TABLE_DATA : "may have"
    TABLE_DATA ||--o{ TABLE_HEADER : "has"
    TABLE_DATA ||--o{ TABLE_ROW : "has"
    TABLE_ROW ||--o{ TABLE_CELL : "has"
    SLIDE_CONTENT ||--o| CHART_DATA : "may have"
    CHART_DATA ||--o{ CHART_SERIES : "has"
    CHART_SERIES ||--o{ CHART_VALUE : "has"
    SLIDE_CONTENT ||--o{ PROCESS_STEP : "may have"
```

---

## Data Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Empty : App launch
    Empty --> Configured : User enters settings
    Configured --> Generating : Click "Generate"
    Generating --> Generated : AI response parsed OK
    Generating --> Fallback : API error / offline mode
    Fallback --> Generated : Sample data loaded
    Generated --> Editing : User edits slide
    Editing --> Generated : Save edits
    Generated --> Downloaded : Click "Download PPTX"
    Downloaded --> [*]
```

