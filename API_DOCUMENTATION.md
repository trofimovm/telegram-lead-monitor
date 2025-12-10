# API Documentation

## Overview

Telegram Lead Monitor API is a RESTful API built with FastAPI that provides endpoints for managing Telegram accounts, monitoring sources, creating rules, and managing leads with LLM-powered analysis.

**Base URL**: `http://localhost:8000` (development)

**API Version**: v1

**API Prefix**: `/api/v1`

## Authentication

### JWT Bearer Token

All protected endpoints require a JWT bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Obtaining a Token

1. **Register a new user**:
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "tenant_name": "My Company"
}
```

2. **Login to get access token**:
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

3. **Use the token in subsequent requests**:
```http
GET /api/v1/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## API Endpoints

### 📝 Authentication

#### Register New User
```http
POST /api/v1/auth/register
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "tenant_name": "My Company"
}
```

**Response**: `200 OK` - User object

---

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

**Request Body**:
```
username=user@example.com&password=securepassword123
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Response**: `200 OK` - Current user object

---

### 📱 Telegram Accounts

#### List Telegram Accounts
```http
GET /api/v1/telegram/accounts
Authorization: Bearer <token>
```

**Response**: `200 OK` - Array of telegram accounts

---

#### Add Telegram Account
```http
POST /api/v1/telegram/accounts
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "phone_number": "+1234567890"
}
```

**Response**: `200 OK` - Telegram account object

---

#### Send Verification Code
```http
POST /api/v1/telegram/accounts/{account_id}/send-code
Authorization: Bearer <token>
```

**Response**: `200 OK` - Code sent confirmation

---

#### Verify Telegram Account
```http
POST /api/v1/telegram/accounts/{account_id}/verify
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "code": "12345"
}
```

**Response**: `200 OK` - Verified account object

---

#### Delete Telegram Account
```http
DELETE /api/v1/telegram/accounts/{account_id}
Authorization: Bearer <token>
```

**Response**: `204 No Content`

---

### 📡 Sources (Telegram Channels/Groups)

#### List Sources
```http
GET /api/v1/telegram/sources?is_active=true
Authorization: Bearer <token>
```

**Query Parameters**:
- `is_active` (boolean, optional): Filter by active status

**Response**: `200 OK` - Array of sources

---

#### Get Source by ID
```http
GET /api/v1/telegram/sources/{source_id}
Authorization: Bearer <token>
```

**Response**: `200 OK` - Source object

---

#### Add Source
```http
POST /api/v1/telegram/sources
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "telegram_account_id": "uuid",
  "telegram_id": 123456789,
  "title": "Startup Jobs",
  "username": "startupjobs",
  "source_type": "channel",
  "is_active": true
}
```

**Response**: `201 Created` - Source object

---

#### Update Source
```http
PATCH /api/v1/telegram/sources/{source_id}
Authorization: Bearer <token>
```

**Request Body** (all fields optional):
```json
{
  "is_active": false,
  "title": "Updated Title"
}
```

**Response**: `200 OK` - Updated source object

---

#### Delete Source
```http
DELETE /api/v1/telegram/sources/{source_id}
Authorization: Bearer <token>
```

**Response**: `204 No Content`

---

#### Sync Available Dialogs
```http
POST /api/v1/telegram/sync-dialogs
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "telegram_account_id": "uuid"
}
```

**Response**: `200 OK`
```json
{
  "synced": 15,
  "dialogs": [...]
}
```

---

### 📋 Rules (Monitoring Rules)

#### List Rules
```http
GET /api/v1/rules?is_active=true
Authorization: Bearer <token>
```

**Query Parameters**:
- `is_active` (boolean, optional): Filter by active status

**Response**: `200 OK` - Array of rules

---

#### Get Rule by ID
```http
GET /api/v1/rules/{rule_id}
Authorization: Bearer <token>
```

**Response**: `200 OK` - Rule object with sources

---

#### Create Rule
```http
POST /api/v1/rules
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "name": "Python Developer Opportunities",
  "description": "Find Python developer job postings",
  "llm_prompt": "Identify job opportunities for Python developers...",
  "match_threshold": 0.7,
  "is_active": true,
  "source_ids": ["uuid1", "uuid2"]
}
```

**Response**: `201 Created` - Rule object

---

#### Update Rule
```http
PATCH /api/v1/rules/{rule_id}
Authorization: Bearer <token>
```

**Request Body** (all fields optional):
```json
{
  "name": "Updated Rule Name",
  "is_active": false,
  "match_threshold": 0.8
}
```

**Response**: `200 OK` - Updated rule object

---

#### Delete Rule
```http
DELETE /api/v1/rules/{rule_id}
Authorization: Bearer <token>
```

**Response**: `204 No Content`

---

### 🎯 Leads

#### List Leads
```http
GET /api/v1/leads?status=new&limit=20&offset=0
Authorization: Bearer <token>
```

**Query Parameters**:
- `status` (string, optional): Filter by status (new, contacted, qualified, converted, rejected)
- `rule_id` (uuid, optional): Filter by rule
- `source_id` (uuid, optional): Filter by source
- `assignee_id` (uuid, optional): Filter by assignee
- `date_from` (datetime, optional): Filter from date
- `date_to` (datetime, optional): Filter to date
- `limit` (int, optional, default: 20): Number of results
- `offset` (int, optional, default: 0): Pagination offset

**Response**: `200 OK` - Array of leads

---

#### Get Lead by ID
```http
GET /api/v1/leads/{lead_id}
Authorization: Bearer <token>
```

**Response**: `200 OK` - Lead object with message and rule details

---

#### Update Lead
```http
PATCH /api/v1/leads/{lead_id}
Authorization: Bearer <token>
```

**Request Body** (all fields optional):
```json
{
  "status": "contacted",
  "notes": "Called and left message",
  "assignee_id": "uuid"
}
```

**Response**: `200 OK` - Updated lead object

---

#### Delete Lead
```http
DELETE /api/v1/leads/{lead_id}
Authorization: Bearer <token>
```

**Response**: `204 No Content`

---

#### Get Lead Statistics
```http
GET /api/v1/leads/stats
Authorization: Bearer <token>
```

**Response**: `200 OK`
```json
{
  "total": 150,
  "recent_count": 25,
  "by_status": {
    "new": 50,
    "contacted": 40,
    "qualified": 30,
    "converted": 20,
    "rejected": 10
  }
}
```

---

#### Export Leads to CSV
```http
GET /api/v1/leads/export/csv?status=new
Authorization: Bearer <token>
```

**Query Parameters**: Same as List Leads

**Response**: `200 OK` - CSV file download

---

### 📊 Analytics

#### Get Analytics Summary
```http
GET /api/v1/analytics/summary?date_from=2024-01-01&date_to=2024-12-31
Authorization: Bearer <token>
```

**Query Parameters**:
- `date_from` (datetime, optional): Start date (default: 30 days ago)
- `date_to` (datetime, optional): End date (default: now)

**Response**: `200 OK`
```json
{
  "total_leads": 150,
  "total_messages": 5000,
  "total_sources": 10,
  "total_rules": 5,
  "avg_lead_score": 0.82,
  "conversion_rate": 3.0,
  "top_source": {...},
  "top_rule": {...},
  "period_start": "2024-01-01T00:00:00",
  "period_end": "2024-12-31T23:59:59"
}
```

---

#### Get Leads Time Series
```http
GET /api/v1/analytics/leads-time-series?granularity=day
Authorization: Bearer <token>
```

**Query Parameters**:
- `date_from` (datetime, optional)
- `date_to` (datetime, optional)
- `granularity` (string, optional): hour, day, week, month (default: day)

**Response**: `200 OK`
```json
{
  "data_points": [
    {
      "timestamp": "2024-01-01T00:00:00",
      "date_label": "2024-01-01",
      "count": 15
    }
  ],
  "period_start": "2024-01-01T00:00:00",
  "period_end": "2024-01-31T23:59:59"
}
```

---

#### Get Conversion Funnel
```http
GET /api/v1/analytics/conversion-funnel
Authorization: Bearer <token>
```

**Response**: `200 OK`
```json
{
  "stages": [
    {
      "stage_name": "new",
      "count": 100,
      "percentage": 100.0,
      "conversion_rate": null
    },
    {
      "stage_name": "contacted",
      "count": 50,
      "percentage": 50.0,
      "conversion_rate": 50.0
    }
  ],
  "final_conversion_rate": 20.0,
  "period_start": "2024-01-01T00:00:00",
  "period_end": "2024-01-31T23:59:59"
}
```

---

#### Get Source Performance
```http
GET /api/v1/analytics/source-performance
Authorization: Bearer <token>
```

**Response**: `200 OK`
```json
{
  "sources": [
    {
      "source_id": "uuid",
      "source_title": "Startup Jobs",
      "total_messages": 1000,
      "total_leads": 50,
      "conversion_rate": 5.0,
      "avg_lead_score": 0.85
    }
  ]
}
```

---

#### Get Rule Performance
```http
GET /api/v1/analytics/rule-performance
Authorization: Bearer <token>
```

**Response**: `200 OK`
```json
{
  "rules": [
    {
      "rule_id": "uuid",
      "rule_name": "Python Jobs",
      "total_leads": 75,
      "leads_last_7d": 10,
      "leads_last_30d": 45,
      "avg_lead_score": 0.82,
      "is_active": true
    }
  ]
}
```

---

#### Get Activity Trends
```http
GET /api/v1/analytics/activity-trends
Authorization: Bearer <token>
```

**Response**: `200 OK`
```json
{
  "period": "Last 7 days vs Previous 7 days",
  "leads_trend": {
    "metric_name": "Leads Created",
    "current_value": 50,
    "previous_value": 42,
    "change_percentage": 19.0,
    "trend_direction": "up"
  },
  "messages_trend": {...},
  "conversion_trend": {...}
}
```

---

### 🔔 Notifications

#### Get Notification Settings
```http
GET /api/v1/notifications/settings
Authorization: Bearer <token>
```

**Response**: `200 OK` - Notification settings object

---

#### Update Notification Settings
```http
PATCH /api/v1/notifications/settings
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "email_notifications": true,
  "notify_on_new_lead": true,
  "notify_on_high_score": true,
  "high_score_threshold": 0.8,
  "notification_email": "user@example.com"
}
```

**Response**: `200 OK` - Updated settings object

---

### 👥 Users (Admin Only)

#### List Users
```http
GET /api/v1/users
Authorization: Bearer <token>
```

**Response**: `200 OK` - Array of users (admin only)

---

#### Update User
```http
PATCH /api/v1/users/{user_id}
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "is_active": false,
  "is_superuser": true
}
```

**Response**: `200 OK` - Updated user (admin only)

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `204 No Content` - Request succeeded with no response body
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Example Error Responses

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**404 Not Found**:
```json
{
  "detail": "Lead not found"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Rate Limiting

Currently, rate limiting is not enforced. In production, consider implementing rate limits to prevent abuse.

---

## Pagination

List endpoints support pagination via `limit` and `offset` query parameters:

```http
GET /api/v1/leads?limit=20&offset=40
```

- `limit`: Number of items to return (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

---

## Interactive Documentation

FastAPI provides interactive API documentation out of the box:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all available endpoints
- See request/response schemas
- Try out API calls directly from the browser
- View detailed parameter descriptions

---

## SDK/Client Libraries

Currently, no official SDK is available. You can use standard HTTP clients:

**JavaScript/TypeScript**:
```javascript
const response = await fetch('http://localhost:8000/api/v1/leads', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const leads = await response.json();
```

**Python**:
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
response = requests.get('http://localhost:8000/api/v1/leads', headers=headers)
leads = response.json()
```

---

## Webhooks

Webhook functionality is not currently implemented but planned for future releases.

---

## Support

For API support and questions, please contact: [your-email]

---

**Last Updated**: 2024-01-01
