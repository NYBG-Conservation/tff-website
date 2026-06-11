# Dataset API Contract (Phase 1)

Base URL (local): `http://localhost:8000`

Authentication:
- Session cookie auth (`credentials: include`) with CSRF.
- Frontend should call `GET /api/accounts/csrf/` before first mutating request.

## Public read API (no authentication)

These endpoints power the public `/research` and `/data` pages.

### `GET /api/public/projects/`
Returns projects where `shared_publicly=true`.

Response fields include: `slug`, `title`, `summary`, `image`, `description_paragraphs`, `dataset_ids`, and PI metadata.

### `GET /api/public/datasets/`
Returns datasets where `expose_on_public_api=true`, status is `active` or `archived`, and the linked project is public (or no project is linked).

Query params:
- `project=<slug>` filter by linked project slug

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

### `GET /api/projects/`
List projects in caller scope.

Query params:
- `mine=true` limit to projects owned by current user
- `organization=<id>` limit by organization
- `shared_publicly=true|false`

### `POST /api/projects/`
Create project.

### `GET /api/projects/{id}/`
Retrieve project if in scope.

### `PATCH /api/projects/{id}/`
Update project if in scope.

Project `slug` is read-only in the API: auto-generated from `short_title` (punctuation removed, spaces as hyphens, max 100 chars before suffix). Collisions get `-1`, `-2`, `-3`, etc.

### `POST /api/projects/{id}/managers/`
Add delegated project manager by username.

Payload:
```json
{ "username": "manager_username" }
```

### `DELETE /api/projects/{id}/managers/{user_id}/`
Remove delegated project manager.

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
- `project` is optional and links dataset to a first-class Project record.
- `data_type` supports: `tabular`, `geospatial`, `image`, `sensor_time_series`, `biodiversity_observation`, `document_archive`.

### `GET /api/datasets/{id}/`
Retrieve single dataset if in scope.

### `PATCH /api/datasets/{id}/`
Update dataset if in scope.

### `POST /api/datasets/{id}/files/`
Upload one file version or register an external asset link.
`multipart/form-data` fields:
- `file` (required unless `external_url` is provided)
- `external_url` (required unless `file` is provided; preferred for assets >1 GB)
- `file_name` (optional)
- `file_kind` (optional, default `primary_data`)
- `content_type` (optional)
- `notes` (optional)

## Upload Governance Policy

- `<= 100 MB`: uploads allowed.
- `100 MB to 1 GB`: uploads allowed, but external links are preferred.
- `> 1 GB`: external link required for dataset assets.
- Publications can be provided as uploaded attachment or external URL/DOI.

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
