# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-19-mvp-demo-system/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Technical Requirements

### Blockchain Infrastructure
- Hyperledger Fabric 2.5+ network with single organization setup for MVP
- JavaScript/TypeScript chaincode implementing contract state machine
- CouchDB state database for complex queries and JSON document storage
- Certificate Authority for identity management and authentication
- Transaction validation and commitment through orderer service

### Odoo Integration
- Custom Odoo 18 addon module with proper manifest and dependencies
- Python models for VendorContract, ContractWorkflow, and VendorProfile
- Three-stage workflow implementation using Odoo's state field functionality
- Role-based access control using Odoo security groups and record rules
- Real-time UI updates through Odoo's web framework and notification system

### API Gateway Architecture
- FastAPI application with async/await pattern for blockchain interactions
- Fabric SDK for Python integration with proper connection profiles
- RESTful endpoints for CRUD operations and workflow state transitions
- Event-driven architecture with webhook notifications from Fabric to Odoo
- Error handling and retry logic for blockchain transaction failures

### Database Design
- PostgreSQL 15+ with proper indexing for contract queries
- Hybrid approach: transactional data in PostgreSQL, immutable records on blockchain
- Foreign key relationships between contracts, vendors, and workflow stages
- Audit logging tables for all state changes and user actions

### User Interface Requirements
- Responsive Odoo views compatible with desktop and tablet interfaces
- Form views for contract creation with field validation and required fields
- Tree/list views with filtering and sorting capabilities for contract management
- Kanban board view showing contracts grouped by workflow stage
- Dashboard widgets displaying contract counts and recent activity

## Approach Options

**Option A: Direct Odoo-Fabric Integration**
- Pros: Simpler architecture, fewer moving parts, direct blockchain calls from Odoo
- Cons: Tight coupling, harder to scale, blockchain dependencies in Odoo core

**Option B: FastAPI Gateway Pattern** (Selected)
- Pros: Loose coupling, independent scaling, API reusability, better error handling
- Cons: Additional service complexity, network latency, more deployment complexity

**Option C: Event-Driven Microservices**
- Pros: Maximum scalability, service independence, fault isolation
- Cons: Over-engineering for MVP, complex orchestration, debugging difficulty

**Rationale:** Option B provides the optimal balance of architectural flexibility and implementation simplicity for the MVP. The FastAPI gateway allows for clean separation of concerns while maintaining manageable complexity for demonstration purposes.

## External Dependencies

- **Hyperledger Fabric SDK for Python** - Blockchain network interaction and transaction management
- **Justification:** Official SDK providing robust connectivity and error handling for Fabric networks

- **Docker & Docker Compose** - Container orchestration for development environment
- **Justification:** Industry standard for consistent development environments and service orchestration

- **FastAPI** - Modern async Python web framework for API gateway
- **Justification:** High performance, automatic API documentation, excellent async support for blockchain interactions

- **asyncpg** - Asynchronous PostgreSQL adapter for FastAPI
- **Justification:** Non-blocking database operations to maintain API responsiveness during blockchain calls

- **psycopg2-binary** - PostgreSQL adapter for Odoo
- **Justification:** Standard Odoo database connector with proven stability

## Performance Considerations

### Blockchain Transaction Optimization
- Implement connection pooling for Fabric gateway connections
- Use async patterns to prevent blocking during transaction submission
- Implement proper timeout handling for blockchain operations (30-second max)
- Cache blockchain query results for read-heavy operations

### Database Optimization
- Create composite indexes on (contract_id, workflow_stage) for efficient filtering
- Implement database connection pooling in FastAPI
- Use prepared statements for frequent contract queries
- Partition audit logs by date for long-term performance

### API Gateway Efficiency
- Implement request/response caching for static contract data
- Use database transactions for maintaining consistency between Odoo and blockchain
- Implement circuit breaker pattern for blockchain unavailability
- Add health check endpoints for all services

## Security Requirements

### Authentication and Authorization
- Leverage Odoo's built-in user authentication system
- Implement API key authentication for FastAPI endpoints
- Use Fabric CA certificates for blockchain identity management
- Role-based access control: Creator, Verificator, and Viewer roles

### Data Protection
- TLS encryption for all inter-service communication
- Secure storage of Fabric certificates and private keys
- Input validation and sanitization for all API endpoints
- SQL injection prevention through ORM usage

### Blockchain Security
- Proper endorsement policies for contract state changes
- Private data collections for sensitive contract information
- Certificate revocation handling for compromised identities
- Transaction replay attack prevention through nonce usage