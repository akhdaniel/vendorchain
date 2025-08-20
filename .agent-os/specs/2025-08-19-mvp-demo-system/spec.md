# Spec Requirements Document

> Spec: MVP Demo System
> Created: 2025-08-19
> Status: Planning

## Overview

Implement a fully functional MVP demonstration system for VendorChain that showcases the complete three-stage contract workflow (Creator → Verificator → Submitted) integrated with Hyperledger Fabric blockchain, accessible through an intuitive Odoo interface. This MVP will serve as a proof-of-concept demonstrating the core value proposition of immutable contract tracking and automated workflows.

## User Stories

### Contract Creation Workflow

As a Procurement Manager, I want to create vendor contracts in Odoo and have them automatically recorded on the blockchain, so that I can establish an immutable audit trail from the moment of contract creation.

**Detailed Workflow:**
1. User logs into Odoo system and navigates to Vendor Contracts module
2. User creates a new contract record with vendor details, contract value, and terms
3. System automatically generates a unique contract ID and initiates blockchain transaction
4. Contract enters "Creator" stage and awaits verification
5. System sends notification to designated verificator

### Contract Verification Process

As a Finance Controller, I want to review and verify contract details before final submission, so that I can ensure all financial terms are accurate and compliant with organizational policies.

**Detailed Workflow:**
1. User receives notification of pending contract verification
2. User reviews contract details in Odoo interface
3. User can approve (moving to "Verificator" stage) or reject (returning to Creator with comments)
4. All verification actions are recorded on the blockchain with timestamps
5. System notifies relevant parties of verification status change

### Contract Submission and Tracking

As a Vendor Representative, I want to view the final submitted contracts and their status, so that I can track contract progress and payment obligations transparently.

**Detailed Workflow:**
1. Verified contracts automatically move to "Submitted" stage
2. Smart contract on blockchain records final submission with immutable timestamp
3. Vendor portal provides read-only access to contract status and payment tracking
4. All parties can view complete audit trail of contract lifecycle
5. System maintains synchronization between Odoo UI and blockchain state

## Spec Scope

1. **Hyperledger Fabric Network Setup** - Complete Docker-based blockchain network with peer nodes, orderer, and certificate authority
2. **Smart Contract Implementation** - JavaScript chaincode handling contract lifecycle with create, verify, and submit functions
3. **Odoo Module Development** - Custom Odoo 18 addon with contract management views, three-stage workflow, and role-based permissions
4. **FastAPI Gateway** - RESTful API service connecting Odoo to Fabric network with real-time synchronization
5. **Database Schema** - PostgreSQL database design supporting contract data, workflow states, and user management
6. **Docker Environment** - Complete containerized development environment with all services orchestrated via Docker Compose
7. **Demonstration Flow** - Working end-to-end demo showcasing contract creation through all three workflow stages

## Out of Scope

- Payment tracking and milestone management (reserved for Phase 3)
- PDF document storage and management (reserved for Phase 3)
- Digital signature integration (reserved for Phase 5)
- Advanced analytics dashboards (reserved for Phase 4)
- Multi-currency support (reserved for Phase 5)
- Production security hardening (reserved for Phase 5)

## Expected Deliverable

1. **Functional Blockchain Network** - Running Hyperledger Fabric network accessible via FastAPI gateway with successful contract transactions
2. **Working Odoo Interface** - Complete three-stage contract workflow demonstrable in browser with role-based access control
3. **Integrated System Demo** - End-to-end demonstration showing contract creation, verification, and submission with blockchain confirmation

## Spec Documentation

- Tasks: @.agent-os/specs/2025-08-19-mvp-demo-system/tasks.md
- Technical Specification: @.agent-os/specs/2025-08-19-mvp-demo-system/sub-specs/technical-spec.md
- API Specification: @.agent-os/specs/2025-08-19-mvp-demo-system/sub-specs/api-spec.md
- Database Schema: @.agent-os/specs/2025-08-19-mvp-demo-system/sub-specs/database-schema.md
- Tests Specification: @.agent-os/specs/2025-08-19-mvp-demo-system/sub-specs/tests.md