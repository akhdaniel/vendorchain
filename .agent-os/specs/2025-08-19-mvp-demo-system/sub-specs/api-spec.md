# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-19-mvp-demo-system/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## FastAPI Gateway Endpoints

### Base Configuration
- **Base URL:** `http://localhost:8000/api/v1`
- **Authentication:** API Key in header (`X-API-Key`)
- **Content-Type:** `application/json`
- **Response Format:** JSON with standard error handling

### Contract Management Endpoints

#### POST /contracts/create

**Purpose:** Create new contract and initiate blockchain transaction
**Parameters:** 
- Request Body: CreateContractRequest model
**Response:** ContractResponse with blockchain transaction ID
**Errors:** 400 (validation), 500 (blockchain failure)

```json
{
  "vendor_id": 1,
  "contract_number": "VCM-2025-0001",
  "contract_value": 50000.00,
  "contract_date": "2025-08-19",
  "expiration_date": "2026-08-19",
  "description": "Software licensing agreement"
}
```

#### PUT /contracts/{contract_id}/verify

**Purpose:** Transition contract from creator to verificator stage
**Parameters:** 
- Path: contract_id (integer)
- Request Body: VerifyContractRequest model
**Response:** ContractResponse with updated workflow stage
**Errors:** 404 (not found), 400 (invalid state), 500 (blockchain failure)

```json
{
  "verificator_notes": "Contract terms reviewed and approved",
  "approved": true
}
```

#### PUT /contracts/{contract_id}/submit

**Purpose:** Final submission of verified contract to blockchain
**Parameters:** 
- Path: contract_id (integer)
- Request Body: SubmitContractRequest model
**Response:** ContractResponse with final blockchain confirmation
**Errors:** 404 (not found), 400 (invalid state), 500 (blockchain failure)

```json
{
  "submission_notes": "Contract finalized and recorded on blockchain"
}
```

#### GET /contracts/{contract_id}

**Purpose:** Retrieve contract details with current blockchain state
**Parameters:** 
- Path: contract_id (integer)
- Query: include_blockchain_state (boolean, default: true)
**Response:** Detailed contract information with workflow history
**Errors:** 404 (not found), 500 (blockchain query failure)

#### GET /contracts

**Purpose:** List contracts with filtering and pagination
**Parameters:** 
- Query: workflow_stage (string), vendor_id (integer), page (integer), limit (integer)
**Response:** Paginated list of contracts
**Errors:** 400 (invalid parameters), 500 (database error)

### Blockchain Interaction Endpoints

#### GET /blockchain/contract/{blockchain_contract_id}

**Purpose:** Query contract state directly from blockchain
**Parameters:** 
- Path: blockchain_contract_id (string)
**Response:** Raw blockchain contract state
**Errors:** 404 (not found on blockchain), 500 (blockchain connection error)

#### GET /blockchain/health

**Purpose:** Check blockchain network connectivity and status
**Parameters:** None
**Response:** Network health status and peer information
**Errors:** 500 (network unavailable)

### Webhook Endpoints

#### POST /webhooks/odoo/contract-updated

**Purpose:** Receive updates from Odoo when contracts are modified
**Parameters:** 
- Request Body: OdooWebhookRequest model
**Response:** Acknowledgment of webhook processing
**Errors:** 400 (invalid payload), 500 (processing error)

#### POST /webhooks/fabric/transaction-committed

**Purpose:** Receive blockchain transaction confirmations
**Parameters:** 
- Request Body: FabricWebhookRequest model
**Response:** Acknowledgment of transaction processing
**Errors:** 400 (invalid transaction), 500 (processing error)

## Odoo XML-RPC API Extensions

### Custom Controllers for Odoo Web Interface

#### /web/dataset/call_kw/vendor.contract.management.contract/create_with_blockchain

**Purpose:** Enhanced contract creation with immediate blockchain integration
**Business Logic:** Validates contract data, creates database record, initiates blockchain transaction via FastAPI
**Error Handling:** Rollback database changes if blockchain transaction fails

#### /web/dataset/call_kw/vendor.contract.management.contract/transition_workflow

**Purpose:** Handle workflow state transitions with blockchain validation
**Business Logic:** Validates user permissions, updates database state, confirms blockchain state consistency
**Error Handling:** Prevents state transitions if blockchain and database are out of sync

### REST API for Vendor Portal

#### GET /api/vendor-portal/contracts

**Purpose:** Read-only access for vendors to view their contracts
**Authentication:** Vendor-specific API keys or portal user authentication
**Response:** Filtered contract list based on vendor identity
**Access Control:** Only contracts where vendor_id matches authenticated vendor

## Data Models

### Request Models

```python
class CreateContractRequest(BaseModel):
    vendor_id: int
    contract_number: str = Field(regex=r"VCM-\d{4}-\d{4}")
    contract_value: Decimal = Field(gt=0)
    contract_date: date
    expiration_date: Optional[date] = None
    description: Optional[str] = None

class VerifyContractRequest(BaseModel):
    verificator_notes: Optional[str] = None
    approved: bool

class SubmitContractRequest(BaseModel):
    submission_notes: Optional[str] = None
```

### Response Models

```python
class ContractResponse(BaseModel):
    id: int
    contract_number: str
    vendor_id: int
    vendor_name: str
    contract_value: Decimal
    workflow_stage: str
    blockchain_tx_id: Optional[str]
    blockchain_contract_id: Optional[str]
    created_date: datetime
    verification_date: Optional[datetime]
    submission_date: Optional[datetime]

class BlockchainHealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    peer_count: int
    latest_block: int
    connection_time_ms: float
```

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Contract number format is invalid",
    "details": {
      "field": "contract_number",
      "expected_format": "VCM-YYYY-NNNN"
    }
  }
}
```

### Error Codes
- **VALIDATION_ERROR:** Input validation failures
- **WORKFLOW_ERROR:** Invalid workflow state transitions
- **BLOCKCHAIN_ERROR:** Blockchain network or transaction failures
- **PERMISSION_ERROR:** Insufficient user permissions
- **NOT_FOUND:** Requested resource does not exist
- **SYNC_ERROR:** Database and blockchain state mismatch

## Authentication and Security

### API Key Management
- Generate unique API keys for each service integration
- Store API keys in environment variables
- Implement key rotation mechanism for security

### Rate Limiting
- 100 requests per minute per API key for standard endpoints
- 10 requests per minute for blockchain query endpoints
- Exponential backoff for failed blockchain transactions

### Request Validation
- JSON schema validation for all request bodies
- SQL injection prevention through parameterized queries
- Input sanitization for all text fields
- File upload validation for future document features

## Integration Patterns

### Odoo to FastAPI Communication
- Use Python requests library with connection pooling
- Implement retry logic with exponential backoff
- Async webhook processing to prevent Odoo blocking
- Circuit breaker pattern for FastAPI unavailability

### FastAPI to Fabric Communication
- Use Fabric SDK for Python with proper error handling
- Implement transaction status polling for confirmation
- Connection pooling for gateway instances
- Timeout handling for blockchain operations (30 seconds max)

### Database Synchronization Strategy
- Immediate database updates for Odoo operations
- Eventual consistency model for blockchain confirmations
- Conflict resolution for concurrent modifications
- Background sync jobs for failed blockchain transactions