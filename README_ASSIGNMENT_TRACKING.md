# Assignment Tracking Implementation

This document describes the implementation of assignment tracking and display functionality for loads, including new headline statistics on the Assigned Loads page.

## Overview

The system now tracks how loads are assigned:
- **Manual (Frontend)**: Assignment performed by an authenticated user through the web UI
- **URL/API (Agent)**: Assignment performed by automated agents or integrations via URL/API

## Backend Changes

### Data Model Updates

#### New Fields Added to Shipment Model

```python
# Assignment tracking fields
assigned_via_url: Optional[bool] = Field(False, description="True if assigned via URL/API, False if assigned manually in frontend")
avg_time_per_call_seconds: Optional[float] = Field(None, ge=0, description="Average time per call in seconds")
```

#### Updated Models

- `ShipmentBase`: Added new fields to base model
- `ShipmentUpdate`: Added new fields for partial updates
- `ShipmentFilters`: Added `assigned_via_url` filter
- `Shipment`: Updated example schema

### API Endpoints

#### New Endpoints

1. **Manual Assignment Endpoint**
   ```
   PATCH /shipments/{shipment_id}/manual
   ```
   - Updates shipment and sets `assigned_via_url = False`
   - Used by frontend for manual assignments

2. **Statistics Endpoint**
   ```
   GET /shipments/stats
   ```
   - Returns statistics split by assignment source
   - Supports same filters as main shipments endpoint
   - Response format:
   ```json
   {
     "manual": {
       "count": 0,
       "total_agreed_price": 0,
       "total_agreed_minus_loadboard": 0,
       "avg_time_per_call_seconds": 0
     },
     "url_api": {
       "count": 0,
       "total_agreed_price": 0,
       "total_agreed_minus_loadboard": 0,
       "avg_time_per_call_seconds": 0
     }
   }
   ```

#### Updated Endpoints

1. **Create Shipment**
   ```
   POST /shipments
   ```
   - Now sets `assigned_via_url = True` (API-based creation)

2. **Update Shipment**
   ```
   PATCH /shipments/{shipment_id}
   ```
   - Now sets `assigned_via_url = True` (API-based update)

3. **Get Shipments**
   ```
   GET /shipments
   ```
   - Added `assigned_via_url` query parameter for filtering

### Assignment Source Logic

#### API/URL Assignments (`assigned_via_url = True`)
- Shipments created via `POST /shipments`
- Shipments updated via `PATCH /shipments/{id}`
- Any direct API calls

#### Manual Assignments (`assigned_via_url = False`)
- Shipments updated via `PATCH /shipments/{id}/manual`
- Historical seed data (backfilled as manual)
- Frontend-initiated changes

### Backfill Implementation

A backfill script (`backend/backfill_assigned_via_url.py`) is provided for migrating existing data:

```bash
# Dry run to see what would be changed
python backend/backfill_assigned_via_url.py --dry-run

# Apply changes
python backend/backfill_assigned_via_url.py
```

The backfill uses heuristics to determine assignment source:
- Load ID patterns (e.g., "API-" prefix)
- Creation date (recent = more likely API)
- Carrier description patterns (e.g., "BOT", "AUTO")

## Frontend Changes

### New Components

#### HeadlineStatsBar
- Displays prominent statistics for Manual vs URL/API assignments
- Shows Average Time per Call prominently
- Includes count, total agreed price, and price difference
- Responsive design with clear visual hierarchy

### Updated Components

#### LoadStatsBar
- Made smaller and less prominent
- Now labeled as "Additional Statistics"
- Reduced font sizes and spacing

### API Integration

#### New Hooks
- `useUpdateShipmentManual()`: For manual frontend updates
- `useShipmentStats()`: For fetching assignment statistics

#### Updated Hooks
- `useToggleShipmentStatus()`: Now uses manual endpoint
- `useUpdateShipment()`: Now uses manual endpoint for frontend updates

### Type Definitions

#### New Types
```typescript
export interface AssignmentStats {
  count: number;
  total_agreed_price: number;
  total_agreed_minus_loadboard: number;
  avg_time_per_call_seconds: number;
}

export interface ShipmentStats {
  manual: AssignmentStats;
  url_api: AssignmentStats;
}
```

#### Updated Types
- `Shipment`: Added `assigned_via_url` and `avg_time_per_call_seconds` fields
- `ShipmentFilters`: Added `assigned_via_url` filter

## Testing

### Backend Tests

Comprehensive test suite in `backend/test_assignment_tracking.py`:

- Assignment source setting on creation/update
- Manual vs API endpoint behavior
- Filtering by assignment source
- Statistics endpoint accuracy
- Filter application in stats

### Test Coverage

- Unit tests for write paths
- API contract tests
- Filter functionality tests
- Statistics calculation tests

## Usage Examples

### Creating a Manual Assignment (Frontend)

```typescript
const updateShipmentManual = useUpdateShipmentManual();

await updateShipmentManual.mutateAsync({
  id: shipmentId,
  data: { status: 'agreed', agreed_price: 1500 }
});
```

### Creating an API Assignment

```bash
curl -X POST http://localhost:8000/shipments \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "load_id": "LD-2025-0001",
    "origin": "Madrid",
    "destination": "Paris",
    "pickup_datetime": "2025-01-15T08:00:00Z",
    "delivery_datetime": "2025-01-16T18:00:00Z"
  }'
```

### Getting Statistics

```typescript
const { data: stats } = useShipmentStats({
  status: 'agreed',
  assigned_via_url: false
});
```

### Filtering by Assignment Source

```typescript
const { data: manualShipments } = useShipments({
  assigned_via_url: false
});
```

## Migration Notes

### For Production Deployment

1. **Database Migration**: If using a real database, create migration to add new columns:
   ```sql
   ALTER TABLE shipments ADD COLUMN assigned_via_url BOOLEAN NOT NULL DEFAULT FALSE;
   ALTER TABLE shipments ADD COLUMN avg_time_per_call_seconds FLOAT;
   ```

2. **Backfill**: Run the backfill script to set historical data:
   ```bash
   python backend/backfill_assigned_via_url.py
   ```

3. **API Updates**: Update any existing API clients to use the new manual endpoint for frontend operations

4. **Frontend Deployment**: Deploy frontend changes to use new statistics display

### Breaking Changes

- New required field `assigned_via_url` in shipment responses
- New endpoint `/shipments/{id}/manual` for manual updates
- Frontend now uses manual endpoint for all user-initiated changes

## Performance Considerations

- Statistics endpoint applies same filters as main endpoint for consistency
- In-memory filtering is used (suitable for demo, consider database indexing for production)
- Frontend caches statistics separately from shipment list for optimal performance

## Future Enhancements

1. **Audit Logging**: Add detailed audit logs for assignment source tracking
2. **Real-time Updates**: WebSocket support for live statistics updates
3. **Advanced Analytics**: Time-series analysis of assignment patterns
4. **User Attribution**: Track which specific user made manual assignments
5. **API Rate Limiting**: Different limits for manual vs automated assignments

## Troubleshooting

### Common Issues

1. **Statistics Not Updating**: Ensure frontend is using manual endpoint for user actions
2. **Filter Not Working**: Check that `assigned_via_url` parameter is properly passed
3. **Backfill Errors**: Review heuristics in backfill script for your specific data patterns

### Debug Endpoints

- `GET /debug`: Shows current database state and shipment counts
- `GET /health`: Basic health check

## Security Considerations

- API key authentication required for all endpoints
- Manual endpoint should only be accessible to authenticated frontend users
- Consider rate limiting for automated vs manual endpoints
- Audit logging recommended for production use
