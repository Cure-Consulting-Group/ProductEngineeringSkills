# Figma REST API Variables & Component Specification

## Authentication & Headers
All requests to the Figma REST API require:
```http
X-Figma-Token: <FIGMA_PERSONAL_ACCESS_TOKEN>
Content-Type: application/json
```

## Variables Endpoint: `POST /v1/files/{file_key}/variables`

### Data Structure:
1. **VariableCollections**: Group variables into thematic domains (e.g. `Brand Colors`, `Device Spacing`).
   - Fields: `action` (`CREATE` | `UPDATE` | `DELETE`), `id`, `name`, `initialModeId`.
2. **Variables**: The individual token slots.
   - Fields: `action`, `id`, `name`, `variableCollectionId`, `resolvedType` (`COLOR` | `FLOAT` | `STRING` | `BOOLEAN`).
3. **VariableModeValues**: Maps a mode (e.g. `Light` vs `Dark`) to a resolved value.
   - For `COLOR`: Values must be normalized float dictionary: `{"r": 0.31, "g": 0.27, "b": 0.90, "a": 1.0}`.
   - For `FLOAT`: Numbers representing pixel values without units (e.g. `16` for `16px`).

## Auto Layout Component Anatomy for Logos

When structuring logo components in Figma:
* **Frame Container**:
  * `layoutMode`: `HORIZONTAL` (Primary) or `VERTICAL` (Stacked).
  * `primaryAxisAlignItems`: `CENTER`.
  * `counterAxisAlignItems`: `CENTER`.
  * `itemSpacing`: Bound to variable `spacing/md`.
  * `paddingLeft`, `paddingRight`, `paddingTop`, `paddingBottom`: Bound to variable `spacing/lg`.
* **Component Variants**:
  * Property: `Type` (`Primary`, `Stacked`, `Icon Only`, `Wordmark Only`).
  * Property: `Theme` (`Default`, `Inverted Dark`, `Monochrome Black`, `Monochrome White`).
