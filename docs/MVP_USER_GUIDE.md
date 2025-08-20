# VendorChain MVP User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Getting Started](#getting-started)
4. [User Roles & Permissions](#user-roles--permissions)
5. [Workflow Guide](#workflow-guide)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

VendorChain is a blockchain-based vendor contract management system that provides:
- **Immutable contract storage** on Hyperledger Fabric blockchain
- **Three-stage workflow**: Created → Verified → Submitted
- **Payment tracking** with complete audit trail
- **Role-based access control** for different user types
- **Real-time synchronization** between database and blockchain

### Key Features
✅ Vendor registration and management  
✅ Contract lifecycle management  
✅ Blockchain immutability  
✅ Payment history tracking  
✅ Expiration reminders  
✅ Complete audit trail  

---

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Odoo UI       │────▶│  FastAPI        │────▶│  Hyperledger    │
│   (Port 8069)   │     │  Gateway        │     │  Fabric         │
│                 │     │  (Port 8000)    │     │  (Port 7051)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────┬───────────┘                       │
                     ▼                                    ▼
              ┌─────────────────┐                ┌─────────────────┐
              │   PostgreSQL    │                │    CouchDB      │
              │   (Port 5432)   │                │   (Port 5984)   │
              └─────────────────┘                └─────────────────┘
```

---

## Getting Started

### 1. System Requirements
- Docker Desktop 4.0+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB free disk space

### 2. Starting the System

```bash
# Clone the repository
git clone <repository-url>
cd vendor-contract-management

# Make scripts executable
chmod +x scripts/*.sh

# Start all services
./scripts/start-mvp.sh
```

### 3. Accessing the System

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| Odoo UI | http://localhost:8069 | admin / admin |
| API Docs | http://localhost:8000/docs | No auth required |
| CouchDB | http://localhost:5984/_utils | admin / adminpw |
| PostgreSQL | localhost:5432 | odoo / odoo |

### 4. First-Time Setup

#### Odoo Configuration
1. Access Odoo at http://localhost:8069
2. Login with admin/admin
3. Go to Apps menu
4. Search for "Vendor Contract Management"
5. Click Install
6. Wait for installation to complete

#### User Setup
1. Go to Settings → Users & Companies → Users
2. Create users for different roles:
   - Procurement Manager (Verifier role)
   - Finance Team (Submitter role)
   - Vendor Manager (Manager role)

---

## User Roles & Permissions

### Role Hierarchy

| Role | Permissions | Typical User |
|------|------------|--------------|
| **User** | View contracts and vendors | All employees |
| **Creator** | Create/edit contracts in CREATED state | Procurement staff |
| **Verifier** | Verify contracts (CREATED → VERIFIED) | Procurement managers |
| **Submitter** | Submit contracts (VERIFIED → SUBMITTED) | Finance team |
| **Manager** | Full system access, terminate contracts | Contract administrators |

### Assigning Roles in Odoo
1. Navigate to Settings → Users & Companies → Users
2. Select user to edit
3. In the "Vendor Contract Management" section, assign appropriate role
4. Save changes

---

## Workflow Guide

### Contract Lifecycle

```
   ┌─────────┐      ┌──────────┐      ┌───────────┐
   │ CREATED │─────▶│ VERIFIED │─────▶│ SUBMITTED │
   └─────────┘      └──────────┘      └───────────┘
        │                │                   │
        └────────────────┴───────────────────┘
                         │
                    ┌──────────┐
                    │ EXPIRED  │
                    └──────────┘
```

### Step-by-Step Workflow

#### 1. Vendor Registration
**Role Required**: Manager

1. Navigate to Vendor Contracts → Vendors → Create
2. Fill in vendor details:
   - Vendor Name
   - Email & Phone
   - Vendor Type (Supplier/Service Provider/Contractor/Consultant)
3. Save to auto-generate Vendor ID
4. System automatically syncs to blockchain

#### 2. Contract Creation
**Role Required**: Creator

1. Navigate to Vendor Contracts → Contracts → Create
2. Select vendor from dropdown
3. Enter contract details:
   - Contract Type
   - Description
   - Total Value
   - Expiry Date
4. Save to auto-generate Contract ID
5. Contract status: **CREATED**

#### 3. Contract Verification
**Role Required**: Verifier

1. Navigate to Vendor Contracts → Contracts → To Verify
2. Open contract to review
3. Click "Verify" button
4. Add verification notes (optional)
5. Contract status: **VERIFIED**

#### 4. Contract Submission
**Role Required**: Submitter

1. Navigate to Vendor Contracts → Contracts → To Submit
2. Open verified contract
3. Click "Submit" button
4. Add submission notes (optional)
5. Contract status: **SUBMITTED**

#### 5. Payment Recording
**Role Required**: Creator or higher

1. Open submitted contract
2. Click "Record Payment" button
3. Enter payment details:
   - Amount
   - Payment Date
   - Reference Number
   - Payment Method
4. Save payment
5. System updates remaining amount

---

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Key Endpoints

#### Health Checks
```bash
# System health
GET /health/

# Database health
GET /health/database

# Blockchain health
GET /health/blockchain
```

#### Vendor Management
```bash
# List vendors
GET /vendors/

# Create vendor
POST /vendors/
{
  "vendor_id": "VENDOR-001",
  "name": "Vendor Name",
  "contact_email": "email@vendor.com",
  "vendor_type": "SUPPLIER",
  "status": "ACTIVE"
}

# Get vendor details
GET /vendors/{vendor_id}
```

#### Contract Management
```bash
# List contracts
GET /contracts/

# Create contract
POST /contracts/
{
  "contract_id": "CONTRACT-001",
  "vendor_id": "VENDOR-001",
  "contract_type": "PURCHASE",
  "description": "Contract description",
  "total_value": 100000,
  "expiry_date": "2025-12-31",
  "created_by": "User Name"
}

# Get contract details
GET /contracts/{contract_id}
```

#### Workflow Operations
```bash
# Verify contract
POST /workflow/contracts/{contract_id}/verify
{
  "verified_by": "Verifier Name",
  "performed_by": "User Name",
  "notes": "Verification notes"
}

# Submit contract
POST /workflow/contracts/{contract_id}/submit
{
  "submitted_by": "Submitter Name",
  "performed_by": "User Name",
  "notes": "Submission notes"
}
```

#### Payment Recording
```bash
# Record payment
POST /contracts/{contract_id}/payments
{
  "amount": 50000,
  "payment_date": "2024-08-19",
  "reference": "PAY-001",
  "method": "Wire Transfer"
}
```

### Interactive API Documentation
Access Swagger UI at: http://localhost:8000/docs

---

## Troubleshooting

### Common Issues & Solutions

#### 1. Services Won't Start
```bash
# Clean up and restart
docker-compose down -v
docker system prune -f
./scripts/start-mvp.sh
```

#### 2. Database Connection Error
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

#### 3. Odoo Module Not Found
1. Ensure addon is in correct directory: `odoo-addon/vendor_contract_management/`
2. Restart Odoo with update flag:
```bash
docker-compose restart odoo
```
3. Update Apps list in Odoo UI

#### 4. API Gateway Not Responding
```bash
# Check logs
docker-compose logs fastapi-gateway

# Restart service
docker-compose restart fastapi-gateway
```

#### 5. Blockchain Sync Issues
```bash
# Check Fabric network
docker-compose logs peer0.org1.vendorchain.com
docker-compose logs orderer.vendorchain.com

# Restart Fabric components
docker-compose restart peer0.org1.vendorchain.com
docker-compose restart orderer.vendorchain.com
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f [service-name]

# Last 100 lines
docker-compose logs --tail=100 [service-name]
```

### Health Check Commands
```bash
# Check all services status
docker-compose ps

# Test database connection
docker-compose exec postgres pg_isready -U odoo

# Test API health
curl http://localhost:8000/api/v1/health/

# Test Odoo
curl http://localhost:8069/web/health
```

---

## Demo Scenarios

### Quick Demo
Run the automated demo script:
```bash
./scripts/run-demo.sh
```

### Manual Demo Steps

1. **Create Vendor**
   - Navigate to Vendors → Create
   - Enter: "TechSupplies Inc."
   - Save

2. **Create Contract**
   - Navigate to Contracts → Create
   - Select vendor
   - Enter value: $250,000
   - Save (Status: CREATED)

3. **Verify Contract**
   - Open contract
   - Click "Verify"
   - Status changes to VERIFIED

4. **Submit Contract**
   - Click "Submit"
   - Status changes to SUBMITTED

5. **Record Payment**
   - Click "Record Payment"
   - Enter $50,000
   - Save

6. **View History**
   - Check Workflow Logs tab
   - See complete audit trail

---

## Support & Resources

### Documentation
- API Documentation: http://localhost:8000/docs
- Hyperledger Fabric: https://hyperledger-fabric.readthedocs.io/
- Odoo Documentation: https://www.odoo.com/documentation/18.0/

### System Maintenance
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Update containers
docker-compose pull
docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U odoo vendorchain > backup.sql

# Restore database
docker-compose exec -T postgres psql -U odoo vendorchain < backup.sql
```

### Performance Tips
1. Allocate at least 4GB RAM to Docker
2. Use SSD storage for better performance
3. Regularly clean unused Docker images: `docker system prune`
4. Monitor resource usage: `docker stats`

---

## Conclusion

VendorChain MVP provides a complete blockchain-based contract management solution with:
- ✅ Secure vendor and contract management
- ✅ Immutable blockchain storage
- ✅ Role-based workflow control
- ✅ Complete audit trail
- ✅ Payment tracking
- ✅ API integration capabilities

For production deployment, consider:
- Setting up proper SSL certificates
- Implementing production-grade authentication
- Configuring backup strategies
- Setting up monitoring and alerting
- Implementing high availability

---

*Version: 1.0.0 | Last Updated: August 2024*