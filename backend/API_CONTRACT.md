# Dataset API Contract (Phase 1)

Base URL (local): `http://localhost:8000`

Authentication:
- Session cookie auth (`credentials: include`) with CSRF.
- Frontend should call `GET /api/accounts/csrf/` before first mutating request.

## Roles

- `internal_admin`: read/write all datasets
- `external_partner_admin`: read/write only owned datasets

## Endpoints

### `GET /api/accounts/csrf/`
Sets CSRF cookie. No auth required.

### `GET /api/accounts/me/`
Returns current user and role.

### `GET /api/organizations/`
List organizations for dataset assignment.

### `GET /api/datasets/`
List datasets in caller scope.

### `POST /api/datasets/`
Create dataset and metadata schema.

Request body example:

```json
{
  "title": "Forest Canopy Survey 2026",
  "description": "Plot-level canopy density observations.",
  "project_id": "forest-inventory-transect-study",
  "cadence": "annual",
  "status": "draft",
  "data_type": "tabular",
  "organization": 1,
  "additional_research_partners": ["Bronx River Alliance"],
  "paper_links": ["https://example.org/paper"],
  "data_collection_start": "2026-01-01",
  "projected_project_end_date": "2028-12-31",
  "metadata_schema_version": 1,
  "metadata_fields": [
    {
      "key": "canopy_percent",
      "label": "Canopy %",
      "field_type": "number",
      "unit": "%",
      "required": true,
      "allowed_values": [],
      "sort_order": 0
    }
  ],
  "metadata_values": [
    { "field_key": "canopy_percent", "value": 42.5 }
  ],
  "publications": [
    {
      "title": "Urban canopy gradients in NYC",
      "citation": "Doe et al. 2025. Journal of Urban Ecology.",
      "doi": "10.1000/example",
      "url": "https://example.org/paper",
      "publication_year": 2025
    }
  ]
}
```

Notes:
- For external users, backend overrides/assigns `owner` to the authenticated user.
- `metadata_values[].field_key` must match a key from `metadata_fields`.
- Value type must match `field_type`.
- `project_id` is optional and links a dataset to frontend research project cards.
- `data_type` supports: `tabular`, `geospatial`, `image`, `sensor_time_series`, `biodiversity_observation`, `document_archive`.

### `GET /api/datasets/{id}/`
Retrieve single dataset if in scope.

### `PATCH /api/datasets/{id}/`
Update dataset if in scope.

### `POST /api/datasets/{id}/files/`
Upload one file version.
`multipart/form-data` fields:
- `file` (required)
- `file_name` (optional)
- `file_kind` (optional, default `primary_data`)
- `content_type` (optional)
- `notes` (optional)

### `GET /api/metadata/field-types/`
Returns available metadata field types.

Example response:

```json
[
  { "value": "text", "label": "Text" },
  { "value": "number", "label": "Number" },
  { "value": "enum", "label": "Enum" }
]
```
