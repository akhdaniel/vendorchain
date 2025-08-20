# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-19-mvp-demo-system/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Test Coverage

### Unit Tests

**VendorContract Model (Odoo)**
- Test contract creation with valid data
- Test contract number format validation (VCM-YYYY-NNNN pattern)
- Test workflow stage transitions (creator → verificator → submitted)
- Test contract value validation (positive numbers only)
- Test date validation (expiration after contract date)
- Test required field validation
- Test unique constraint on contract_number

**ContractWorkflowLog Model (Odoo)**
- Test workflow log creation on stage transitions
- Test automatic timestamp setting
- Test user tracking for workflow changes
- Test blockchain transaction ID recording

**VendorProfile Model (Odoo)**
- Test vendor creation with required fields
- Test unique constraint on vendor_code
- Test email format validation
- Test phone number format handling

**FastAPI Service Classes**
- Test ContractService.create_contract() method
- Test ContractService.transition_workflow() method
- Test BlockchainService.submit_transaction() method
- Test BlockchainService.query_contract_state() method
- Test DatabaseService.sync_blockchain_state() method

**Smart Contract (Chaincode)**
- Test CreateContract function with valid parameters
- Test VerifyContract function state transition logic
- Test SubmitContract function finalization
- Test QueryContract function with existing contract ID
- Test error handling for invalid contract states
- Test access control for contract modifications

### Integration Tests

**Odoo to FastAPI Integration**
- Test contract creation flow from Odoo UI to blockchain
- Test workflow transition API calls with authentication
- Test error handling when FastAPI is unavailable
- Test webhook processing for blockchain confirmations
- Test database rollback on blockchain transaction failures

**FastAPI to Fabric Integration**
- Test blockchain transaction submission and confirmation
- Test contract state queries from chaincode
- Test connection handling and retry logic
- Test transaction timeout scenarios
- Test network peer failures and recovery

**Database Integration**
- Test CRUD operations for all contract models
- Test foreign key constraints and referential integrity
- Test database triggers for automatic timestamps
- Test concurrent access and transaction isolation
- Test backup and restore procedures

**End-to-End Workflow Tests**
- Complete contract lifecycle: creation → verification → submission
- Multi-user workflow with different roles (creator, verificator)
- Error scenarios: invalid data, network failures, permission errors
- Performance testing with multiple concurrent contracts
- Data consistency verification between database and blockchain

### Feature Tests

**Contract Creation Feature**
- User can access contract creation form in Odoo
- Form validation displays appropriate error messages
- Successful creation shows confirmation and contract number
- New contract appears in contract list with "creator" stage
- Blockchain transaction is initiated and confirmed

**Contract Verification Feature**
- Verificator can see pending contracts in verification queue
- Verification form allows approval/rejection with notes
- Approved contracts transition to "verificator" stage
- Rejected contracts return to "creator" with feedback
- All verification actions are logged with timestamps

**Contract Submission Feature**
- Verified contracts automatically move to submission queue
- Final submission requires confirmatory action
- Submitted contracts show final blockchain confirmation
- Contract status becomes read-only after submission
- Complete audit trail is accessible for all stages

**Vendor Portal Access**
- Vendors can log in to dedicated portal interface
- Portal displays only contracts for authenticated vendor
- Contract details are read-only for vendor users
- Payment status and workflow progress are visible
- Historical contract information is accessible

**Role-Based Security**
- Creator role can create and edit own contracts
- Verificator role can only verify contracts in pending stage
- Viewer role has read-only access to all contracts
- Unauthorized users cannot access restricted functions
- API endpoints respect role-based permissions

### Performance Tests

**Database Performance**
- Contract queries with filtering and pagination (< 500ms)
- Bulk contract creation (100 contracts in < 30 seconds)
- Complex reporting queries (< 2 seconds)
- Database backup and restore operations
- Index effectiveness for common query patterns

**Blockchain Performance**
- Single contract transaction submission (< 10 seconds)
- Contract state queries (< 3 seconds)
- Concurrent transaction handling (10 simultaneous)
- Network recovery after peer failures
- Transaction throughput measurement

**API Performance**
- FastAPI endpoint response times (< 1 second)
- Concurrent API requests handling (50 simultaneous)
- Large payload processing (complex contract data)
- Error response time consistency
- API gateway connection pooling efficiency

## Mocking Requirements

### Blockchain Network Mocking
- **Hyperledger Fabric Test Network:** Use test-network configuration for development testing
- **Mock Fabric Gateway:** Create mock gateway for unit tests that simulates blockchain responses
- **Transaction Simulation:** Mock successful and failed transaction scenarios
- **Network Latency Simulation:** Configurable delays for testing timeout handling

### External Service Mocking
- **Odoo Database Connections:** Use test database with sample data for integration tests
- **Email Service:** Mock SMTP server for notification testing
- **File Storage:** Mock file system or S3 service for document handling
- **Time-Based Tests:** Mock system time for testing contract expiration logic

### Test Data Management
- **Database Seeding:** Automated test data creation for consistent test environments
- **Blockchain State:** Predefined contract states on test blockchain
- **User Fixtures:** Test users with different roles and permissions
- **Contract Templates:** Standard contract data for various test scenarios

### Mock Services Implementation

```python
# Mock Fabric Gateway for Unit Tests
class MockFabricGateway:
    def submit_transaction(self, contract_id, function, args):
        # Simulate blockchain transaction
        return {"tx_id": f"mock_tx_{contract_id}", "status": "committed"}
    
    def evaluate_transaction(self, contract_id, function, args):
        # Simulate blockchain query
        return {"contract_id": contract_id, "stage": "creator", "value": 50000}

# Mock Odoo Environment for API Tests
class MockOdooEnv:
    def __init__(self):
        self.contracts = {}
        self.users = {}
    
    def create_contract(self, vals):
        # Simulate Odoo record creation
        contract_id = len(self.contracts) + 1
        self.contracts[contract_id] = vals
        return contract_id
```

## Test Environment Setup

### Docker Test Configuration
- Separate docker-compose.test.yml for isolated testing
- Test-specific environment variables
- Cleanup procedures for test data
- Parallel test execution support

### Continuous Integration
- GitHub Actions workflow for automated testing
- Test result reporting and coverage metrics
- Failed test notification and debugging information
- Performance regression detection

### Test Data Isolation
- Database transaction rollback after each test
- Blockchain test network reset procedures
- File system cleanup for uploaded documents
- Redis cache clearing for session tests

## Coverage Targets

### Code Coverage Goals
- **Unit Tests:** 90% code coverage minimum
- **Integration Tests:** 80% pathway coverage
- **Feature Tests:** 100% user story coverage
- **API Tests:** 100% endpoint coverage

### Quality Gates
- All tests must pass before deployment
- No decrease in code coverage percentage
- Performance tests must meet response time requirements
- Security tests must pass vulnerability scans
- Documentation must be updated with test procedures