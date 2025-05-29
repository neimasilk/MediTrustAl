# MediTrustAl Architecture Document

## System Architecture Overview

### Components
```
MediTrustAl
├── Frontend (React.js)
│   ├── Patient Portal
│   ├── Doctor Portal
│   └── Admin Portal
├── Backend (FastAPI)
│   ├── API Gateway
│   ├── Auth Service
│   ├── Medical Records Service
│   └── Blockchain Service
├── Database (PostgreSQL 15)
│   ├── User Data
│   ├── Medical Records
│   └── Audit Logs
└── Blockchain (Ganache → Hyperledger)
    ├── Smart Contracts
    └── DID Registry
```

### Data Flow
1. **Authentication Flow**
   ```
   Client → API Gateway → Auth Service → Database
                                    └→ Blockchain (DID)
   ```

2. **Medical Record Flow**
   ```
   Client → API Gateway → Medical Records Service → Database (Encrypted Data)
                                                └→ Blockchain (Hash + Access Control)
   ```

3. **Consent Flow**
   ```
   Patient → API Gateway → Medical Records Service → Smart Contract
   Doctor  → API Gateway → Medical Records Service → Smart Contract → Database
   ```

### Security Architecture
```
External Request
       ↓
[Rate Limiter]
       ↓
[WAF/DDOS Protection]
       ↓
[API Gateway]
       ↓
[JWT Validation]
       ↓
[RBAC Check]
       ↓
[Service Layer]
       ↓
[Data Layer]
```

### Database Architecture
```
Connection Pool (20 max)
       ↓
[Primary DB] ←→ [Read Replica 1]
     ↓
[Backup System]
```

### Blockchain Architecture

**Note:** For the demoed MVP, interaction will occur with Ganache and smart contracts already deployed locally.
```
Development/MVP:
[Ganache Local Node]
       ↓
[Hardhat Development Environment]  # As per tech-stack.md which recommends Hardhat
       ↓
[Smart Contracts (Solidity)]

Production (Future):
[Hyperledger Fabric]
       ↓
[Chaincode (Go/Java)]
       ↓
[Channels]
```

**Migration Notes:**
- An abstraction layer will be developed to facilitate the transition from Ganache/Ethereum to Hyperledger Fabric.
- Migration testing will be conducted in a staging environment before production implementation.
- The transition will be carried out gradually according to the migration plan in tech-stack.md.

### Monitoring Architecture
```
Application Logs → CloudWatch
Metrics → Prometheus → Grafana
Traces → Jaeger
Alerts → PagerDuty
```

### AI/NLP Architecture
```
[Medical Records]
       ↓
[Data Preprocessing]
       ↓
[NLP Pipeline]
├── Text Extraction
├── Entity Recognition  # Currently a placeholder; planned for MVP via DeepSeek API (Initial MVP implementation uses DeepSeek API, further development for other NLP features will follow)
├── Relation Extraction
└── Text Classification
       ↓
[AI Models]
├── Risk Prediction
├── Treatment Recommendation
└── Outcome Analysis
       ↓
[Model Registry]
       ↓
[Inference Service]
```

### PIPL Compliance Architecture
```
[Data Collection]
       ↓
[Consent Management]
       ↓
[Data Classification]
├── Personal Information
├── Sensitive Personal Information
└── Medical Data
       ↓
[Access Control]
├── Role-Based Access
├── Purpose-Based Access
└── Time-Based Access
       ↓
[Data Processing]
├── Encryption
├── Anonymization
└── Pseudonymization
       ↓
[Audit Trail]
       ↓
[Data Deletion]
```

### Data Retention Policies
```yaml
Personal Information:
  standard_retention: 5 years
  extended_retention: 10 years
  retention_triggers:
    - last_access_date
    - last_update_date
    - consent_withdrawal_date

Medical Records:
  diagnostic_reports: 15 years
  treatment_records: 20 years
  imaging_data: 10 years
  lab_results: 10 years
  retention_triggers:
    - last_treatment_date
    - patient_request_date
    - legal_requirement_date

Audit Logs:
  access_logs: 3 years
  change_logs: 5 years
  security_logs: 7 years
  retention_triggers:
    - regulatory_requirement
    - security_incident
    - legal_hold

Backup Data:
  daily_backups: 30 days
  weekly_backups: 90 days
  monthly_backups: 1 year
  yearly_backups: 7 years

Data Deletion Process:
  soft_delete_period: 30 days
  hard_delete_schedule: quarterly
  deletion_verification: required
  deletion_documentation: 7 years
```

## Integration Points

### External Systems
1. **Hospital Systems**
   - Protocol: HL7 FHIR R4
   - Authentication: OAuth 2.0
   - Data Format: JSON

2. **Payment Gateway**
   - Protocol: REST
   - Authentication: API Key
   - Encryption: TLS 1.3

### Internal Services
1. **Service Discovery**
   - Method: Kubernetes Service
   - Health Check: /health
   - Readiness: /ready

2. **Message Queue**
   - System: RabbitMQ
   - Exchanges: 
     * medical.events
     * blockchain.events
   - Queues:
     * medical.records.created
     * blockchain.transactions

## Scaling Strategy

### Horizontal Scaling
```yaml
Frontend:
  min_replicas: 2
  max_replicas: 10
  cpu_threshold: 70%

Backend:
  min_replicas: 3
  max_replicas: 15
  cpu_threshold: 70%

Database:
  primary: 1
  replicas: 2
```

### Vertical Scaling
```yaml
Frontend:
  cpu: 1
  memory: 2Gi

Backend:
  cpu: 2
  memory: 4Gi

Database:
  cpu: 4
  memory: 8Gi
```

## Disaster Recovery

### Backup Strategy
1. **Database**
   - Full backup: Daily
   - WAL shipping: Continuous
   - Retention: 30 days

2. **Blockchain**
   - Node snapshots: Daily
   - State backup: Weekly
   - Contract state: Every deployment

### Recovery Strategy
1. **RTO (Recovery Time Objective)**
   - Critical systems: 1 hour
   - Non-critical: 4 hours

2. **RPO (Recovery Point Objective)**
   - Database: 5 minutes
   - Blockchain: 1 block

## Performance Requirements

### Response Times
```yaml
API Endpoints:
  p95: 300ms
  p99: 500ms

Database Queries:
  p95: 100ms
  p99: 200ms

Blockchain Transactions:
  p95: 2s
  p99: 5s
```

### Throughput
```yaml
API Requests:
  sustained: 1000 rps
  peak: 2000 rps

Database:
  reads: 5000 qps
  writes: 1000 qps

Blockchain:
  transactions: 100 tps
```

### Resource Limits
```yaml
Memory:
  frontend: 2GB per instance
  backend: 4GB per instance
  database: 8GB per instance

Storage:
  database: 500GB
  blockchain: 1TB
  backups: 2TB
```

## CI/CD Architecture

### Environments
```
Development → Staging → Production
     ↓           ↓          ↓
  dev.ai     staging.ai   prod.ai
```

### Pipeline Stages
```
[Code Push] → [Build] → [Test] → [Security Scan] → [Deploy]
     ↓          ↓        ↓           ↓               ↓
   Git CI    Docker    Jest      SAST/DAST     Kubernetes
            Build     PyTest     Snyk/SonarQube  Helm
```

### Environment Configuration
```yaml
Development:
  domain: dev.meditrustal.ai
  ssl: self-signed
  blockchain: ganache
  monitoring: basic

Staging:
  domain: staging.meditrustal.ai
  ssl: lets-encrypt
  blockchain: ganache
  monitoring: full

Production:
  domain: meditrustal.ai
  ssl: commercial
  blockchain: hyperledger
  monitoring: full + alerts
```

### Backup Synchronization
```
[Database Backup]     [Blockchain Backup]
       ↓                     ↓
[Transaction Log]   [Block Snapshot]
       ↓                     ↓
[Point-in-Time Recovery]  [State Recovery]
       ↓                     ↓
[Consistency Check]
```