# VendorChain - Blockchain Vendor Contract Management System

## Agent OS Documentation

### Product Context
- **Mission & Vision:** @.agent-os/product/mission.md
- **Technical Architecture:** @.agent-os/product/tech-stack.md
- **Development Roadmap:** @.agent-os/product/roadmap.md
- **Decision History:** @.agent-os/product/decisions.md

### Development Standards
- **Code Style:** @~/.agent-os/standards/code-style.md
- **Best Practices:** @~/.agent-os/standards/best-practices.md

### Project Management
- **Active Specs:** @.agent-os/specs/
- **Spec Planning:** Use `@~/.agent-os/instructions/create-spec.md`
- **Tasks Execution:** Use `@~/.agent-os/instructions/execute-tasks.md`

## Workflow Instructions

When asked to work on this codebase:

1. **First**, check @.agent-os/product/roadmap.md for current priorities
2. **Then**, follow the appropriate instruction file:
   - For new features: @~/.agent-os/instructions/create-spec.md
   - For tasks execution: @~/.agent-os/instructions/execute-tasks.md
3. **Always**, adhere to the standards in the files listed above

## Important Notes

- Product-specific files in `.agent-os/product/` override any global standards
- User's specific instructions override (or amend) instructions found in `.agent-os/specs/...`
- Always adhere to established patterns, code style, and best practices documented above.

## Project Structure

This is a monorepo containing:
- `/odoo-addon` - Odoo 18 custom module for vendor contract management
- `/fastapi-gateway` - FastAPI service connecting Odoo to Hyperledger Fabric
- `/fabric-network` - Hyperledger Fabric network configuration and setup
- `/chaincode` - Smart contracts for vendor contract management
- `/docker` - Docker Compose configurations for the entire stack

## Key Technical Components

1. **Hyperledger Fabric Network**: Multi-org blockchain network with peers, orderers, and CAs
2. **Smart Contracts**: JavaScript/TypeScript chaincode managing contract lifecycle
3. **Odoo Integration**: Custom Odoo 18 module with vendor contract models and workflows
4. **API Gateway**: FastAPI service providing REST endpoints and Fabric SDK integration
5. **PostgreSQL Database**: Storing Odoo data and off-chain contract metadata

## Development Workflow

1. **Setup**: Initialize Docker environment and Fabric network (Phase 1 of roadmap)
2. **Contract Workflow**: Implement Creator → Verificator → Submitted flow
3. **Payment Tracking**: Add payment history and balance management
4. **Vendor Portal**: Provide read-only access for vendors
5. **Analytics**: Build dashboards for contract and vendor performance

## Current Focus

Starting with Phase 1: Foundation & Infrastructure
- Docker environment setup
- Hyperledger Fabric network initialization
- Basic project structure creation