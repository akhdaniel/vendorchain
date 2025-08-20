# Technical Stack

> Last Updated: 2025-08-19
> Version: 1.0.0

## Core Technologies

### Blockchain Platform
- **Framework:** Hyperledger Fabric
- **Version:** 2.5+
- **Network:** Multi-org network with peer nodes, orderers, and CAs

### Application Framework
- **ERP Platform:** Odoo
- **Version:** 18.0
- **Language:** Python 3.11+

### API Gateway
- **Framework:** FastAPI
- **Version:** 0.100+
- **Language:** Python 3.11+

### Database
- **Primary:** PostgreSQL
- **Version:** 15+
- **Usage:** Odoo data, FastAPI metadata, off-chain storage

## Frontend Stack

### Odoo Frontend
- **Framework:** Odoo Web Framework (OWL)
- **Version:** Native Odoo 18
- **Build Tool:** Odoo Assets

### JavaScript Framework
- **Framework:** Vue.js (for custom components if needed)
- **Version:** 3.x
- **Package Manager:** npm

### CSS Framework
- **Framework:** Bootstrap (Odoo default)
- **Version:** 5.x
- **Custom Styling:** SCSS

### UI Components
- **Library:** Odoo Native Components
- **Custom Components:** Vue.js based widgets
- **Charts:** Chart.js for dashboards

## Blockchain Infrastructure

### Hyperledger Fabric Components
- **Peer Nodes:** 2+ per organization
- **Orderer:** Raft consensus (3+ nodes)
- **Certificate Authority:** Fabric CA
- **CouchDB:** State database for peers

### Smart Contract Development
- **Language:** JavaScript/TypeScript (Node.js chaincode)
- **SDK:** Fabric SDK for Python
- **Version:** fabric-sdk-py 1.0+

## Assets & Media

### Document Storage
- **Provider:** Local filesystem initially
- **Future:** Amazon S3 or IPFS
- **Format Support:** PDF, DOCX, images

### Fonts
- **Provider:** System fonts
- **Loading Strategy:** Odoo default

### Icons
- **Library:** Font Awesome (Odoo default)
- **Implementation:** Icon fonts

## Infrastructure

### Development Environment
- **Containerization:** Docker
- **Orchestration:** Docker Compose
- **Version:** Docker 24+, Compose 2.20+

### Application Hosting
- **Platform:** On-premise initially
- **Container Platform:** Docker Swarm or Kubernetes (future)
- **Region:** Customer-defined

### Database Hosting
- **Provider:** Self-hosted PostgreSQL
- **Container:** Official PostgreSQL Docker image
- **Backups:** Daily automated via pg_dump

### Blockchain Network Hosting
- **Environment:** Docker containers
- **Network:** Bridge network for development
- **Production:** Multi-host overlay network

## Deployment

### CI/CD Pipeline
- **Platform:** GitHub Actions
- **Trigger:** Push to main/develop branches
- **Tests:** Unit tests, integration tests, chaincode tests

### Container Registry
- **Provider:** Docker Hub or GitHub Container Registry
- **Images:** Odoo, FastAPI, Fabric peer/orderer/CA

### Environments
- **Development:** Docker Compose local
- **Staging:** Docker Compose on staging server
- **Production:** Docker Swarm/Kubernetes

## Development Tools

### Version Control
- **Platform:** Git
- **Repository:** GitHub
- **Strategy:** Git Flow

### API Documentation
- **Tool:** Swagger/OpenAPI (FastAPI automatic)
- **Format:** JSON/YAML
- **UI:** Swagger UI

### Testing Frameworks
- **Python:** pytest, unittest
- **JavaScript:** Jest (for chaincode)
- **Integration:** Postman/Newman

## Security

### Authentication
- **Odoo:** Native session-based auth
- **API:** JWT tokens
- **Blockchain:** X.509 certificates

### Encryption
- **TLS:** All network communication
- **Data at Rest:** PostgreSQL encryption
- **Blockchain:** Fabric private data collections

## Monitoring

### Application Monitoring
- **Logs:** Docker logs, Odoo logs
- **Metrics:** Prometheus (future)
- **Visualization:** Grafana (future)

### Blockchain Monitoring
- **Explorer:** Hyperledger Explorer
- **Metrics:** Fabric metrics via Prometheus
- **Logs:** Peer and orderer logs

## Code Repository URL
- **URL:** To be determined
- **Structure:** Monorepo with /odoo-addon, /fastapi-gateway, /fabric-network, /chaincode