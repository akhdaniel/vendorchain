# VendorChain - Blockchain-Powered Vendor Contract Management

## Overview

VendorChain is a comprehensive vendor contract management system that combines enterprise ERP capabilities with blockchain immutability. Built with Odoo 18 ERP and Hyperledger Fabric blockchain, it provides a complete solution for managing vendor relationships, contracts, and payments with full traceability.

## Features

### Core Functionality
- **Vendor Management**: Complete vendor lifecycle management with blockchain identity
- **Contract Workflow**: Three-stage workflow (Created → Verified → Submitted)
- **Payment Tracking**: Detailed payment history with blockchain transaction IDs
- **Blockchain Integration**: Every action recorded on Hyperledger Fabric
- **Odoo 18 ERP**: Full ERP capabilities with custom module

### Blockchain Features
- **Immutable Audit Trail**: All contract operations recorded on blockchain
- **Transaction IDs**: Every operation gets a unique blockchain transaction ID
- **Vendor Identity**: Each vendor has a unique blockchain address
- **Smart Contracts**: Chaincode for vendor and contract management

### User Interface
- **Modern Dashboard**: Real-time analytics and statistics
- **Payment History**: List view of all payments with filtering
- **Workflow Tracking**: Visual workflow with blockchain verification
- **Document Management**: Attach and manage contract documents

## Technology Stack

### Backend
- **ERP System**: Odoo 18
- **API Gateway**: FastAPI (Python)
- **Blockchain**: Hyperledger Fabric 2.5.4
- **Database**: PostgreSQL 15
- **Caching**: Redis (optional)

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Operating System**: Linux/macOS/Windows with Docker
- **Python**: 3.11+
- **Node.js**: 18+ (for Fabric tools)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git installed
- 8GB+ RAM recommended
- Ports available: 5432, 5984, 7050, 7051, 8000, 8069

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/akhdaniel/vendorchain.git
cd vendorchain
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Wait for services to initialize** (about 2-3 minutes)
```bash
docker-compose ps
```

4. **Access the applications**
- Odoo ERP: http://localhost:8069
  - Username: `admin`
  - Password: `admin`
- API Documentation: http://localhost:8000/docs
- CouchDB: http://localhost:5984/_utils
  - Username: `admin`
  - Password: `adminpw`

## Project Structure

```
vendorchain/
├── docker-compose.yml           # Multi-service orchestration
├── .env                         # Environment variables
├── odoo-addon/                  # Odoo custom module
│   └── vendor_contract_management/
│       ├── models/              # Data models
│       ├── views/               # UI views
│       ├── wizard/              # Wizards (payment, etc.)
│       └── security/            # Access control
├── fastapi-gateway/             # API Gateway
│   └── app/
│       ├── main.py             # FastAPI application
│       ├── routers/            # API endpoints
│       └── models.py           # Database models
├── fabric-network/              # Hyperledger Fabric config
│   ├── configtx.yaml           # Network configuration
│   ├── docker-compose-fabric.yaml
│   └── chaincode/              # Smart contracts
├── postgres-db/                 # Database initialization
│   └── init-scripts/
└── scripts/                     # Utility scripts
    ├── start-all.sh            # Start everything
    ├── stop-all.sh             # Stop everything
    └── test-*.py               # Test scripts
```

## Usage

### Creating a Vendor
1. Navigate to **Vendor Contracts → Vendors**
2. Click **New**
3. Fill in vendor details
4. Save to generate blockchain identity

### Creating a Contract
1. Navigate to **Vendor Contracts → Contracts**
2. Click **New**
3. Select vendor and enter contract details
4. Save to create contract on blockchain

### Processing Workflow
1. Open a contract
2. Click **Verify Contract** (requires verifier role)
3. Click **Submit Contract** (requires submitter role)
4. Each action creates a blockchain transaction

### Recording Payments
1. Open a submitted contract
2. Click **Record Payment**
3. Enter payment details
4. Submit to record on blockchain
5. View payment history via the **Payments** button

## Testing

Run test scripts to verify functionality:

```bash
# Test payment functionality
python3 scripts/test-payment-history-view.py

# Test blockchain transaction IDs
python3 scripts/test-blockchain-tx-ids.py

# Test vendor blockchain fields
python3 scripts/test-vendor-blockchain.py

# Run comprehensive demo
./scripts/mvp-final-demo.sh
```

## API Endpoints

Key API endpoints (http://localhost:8000/docs):

- `GET /health` - System health check
- `POST /vendors` - Create vendor
- `GET /vendors/{vendor_id}` - Get vendor details
- `POST /contracts` - Create contract
- `GET /contracts/{contract_id}` - Get contract
- `POST /contracts/{contract_id}/verify` - Verify contract
- `POST /contracts/{contract_id}/submit` - Submit contract
- `POST /contracts/{contract_id}/payments` - Record payment

## Security

### User Roles
- **User**: View-only access
- **Creator**: Create vendors and contracts
- **Verifier**: Verify contracts
- **Submitter**: Submit contracts
- **Manager**: Full access

### Blockchain Security
- Immutable transaction history
- Cryptographic transaction IDs
- Tamper-proof audit trail

## Development

### Running in Development Mode

```bash
# Start with logs
docker-compose up

# View logs for specific service
docker logs -f vendorchain-odoo
docker logs -f vendorchain-fastapi

# Access Odoo shell
docker exec -it vendorchain-odoo odoo shell -d vendorchain
```

### Updating Odoo Module

```bash
# Update module after changes
docker exec vendorchain-odoo odoo -c /etc/odoo/odoo.conf -u vendor_contract_management --stop-after-init

# Or restart Odoo
docker restart vendorchain-odoo
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change ports in docker-compose.yml
   - Or stop conflicting services

2. **Odoo module not loading**
   - Check logs: `docker logs vendorchain-odoo`
   - Restart Odoo: `docker restart vendorchain-odoo`

3. **Blockchain not syncing**
   - Check Fabric peer: `docker logs fabric-peer`
   - Ensure CouchDB is running: `docker ps | grep couch`

### Reset Everything

```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: Deletes all data)
docker-compose down -v

# Start fresh
docker-compose up -d
```

## Documentation

- [Payment History Implementation](PAYMENT_HISTORY_UPDATE.md)
- [Blockchain Transaction IDs](BLOCKCHAIN_TX_ID_FIX.md)
- [Vendor Blockchain Fields](VENDOR_BLOCKCHAIN_FIELDS.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/akhdaniel/vendorchain/issues
- Documentation: See `/docs` folder

## Acknowledgments

- Odoo Community for the ERP framework
- Hyperledger team for Fabric blockchain
- FastAPI for the modern API framework

---

**VendorChain** - Bringing trust and transparency to vendor management through blockchain technology.