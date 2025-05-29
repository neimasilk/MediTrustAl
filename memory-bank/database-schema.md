# Database Schema Documentation

## Overview

MediTrustAl uses PostgreSQL as its primary database to store application data. The database schema is designed to support blockchain integration and meet authentication and medical data management needs.

## Tables

### 1. users
Stores user information and authentication credentials.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    blockchain_address VARCHAR(42) UNIQUE,  -- Ethereum address format
    role VARCHAR(20) NOT NULL CHECK (role IN ('PATIENT', 'DOCTOR', 'ADMIN')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_blockchain_address ON users(blockchain_address);
```

### 2. sessions
(Note: The sessions table is currently not implemented in Alembic migrations. Its relevance will be reviewed for future refresh token implementation or server-side session management.)
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_valid BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_refresh_token ON sessions(refresh_token);
```

### 3. medical_records
```sql
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    blockchain_record_id VARCHAR(66) UNIQUE NOT NULL,  -- Ethereum transaction hash (tx_hash) generated when recording data_hash to the blockchain. This is the transaction ID on the blockchain.
    record_type VARCHAR(50) NOT NULL CHECK (record_type IN (
        'DIAGNOSIS',
        'LAB_RESULT',
        'PRESCRIPTION',
        'TREATMENT_PLAN',
        'MEDICAL_HISTORY',
        'VITAL_SIGNS',
        'IMAGING',
        'VACCINATION'
    )),
    record_metadata JSONB,  -- Additional metadata specific to record type (consistent with ORM and Pydantic model names)
    encrypted_data BYTEA NOT NULL, -- Encrypted FHIR R4 data (AES-256-GCM suggested)
    data_hash VARCHAR(64) NOT NULL,  -- SHA-256 hash of unencrypted data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX idx_medical_records_blockchain_record_id ON medical_records(blockchain_record_id);
CREATE INDEX idx_medical_records_record_type ON medical_records(record_type);
CREATE INDEX idx_medical_records_record_metadata ON medical_records USING gin (record_metadata);
```

#### Record Types Documentation

1. **DIAGNOSIS**
   - Diagnosis codes (ICD-10)
   - Diagnosis description
   - Diagnosing doctor
   - Date of diagnosis

2. **LAB_RESULT**
   - Test type
   - Test results
   - Reference ranges
   - Lab facility information

3. **PRESCRIPTION**
   - Medication details
   - Dosage instructions
   - Duration
   - Prescribing doctor

4. **TREATMENT_PLAN**
   - Treatment objectives
   - Procedures
   - Timeline
   - Expected outcomes

5. **MEDICAL_HISTORY**
   - Past conditions
   - Surgeries
   - Family history
   - Allergies

6. **VITAL_SIGNS**
   - Blood pressure
   - Heart rate
   - Temperature
   - Respiratory rate
   - Other measurements

7. **IMAGING**
   - Image type (X-ray, MRI, CT, etc.)
   - Body part
   - Findings
   - Radiologist notes

8. **VACCINATION**
   - Vaccine type
   - Date administered
   - Batch number
   - Next dose due date

## Indexing Strategy

1. **Primary Keys**
   - Using UUID for primary keys (with gen_random_uuid())
   - Provides better scalability for distributed systems
   - Avoids potential conflicts when merging data from various sources

2. **Foreign Keys**
   - Always use foreign key constraints to maintain referential integrity
   - Index on foreign key columns for JOIN operation optimization

3. **Unique Constraints**
   - Email and username in the users table
   - Blockchain address to prevent duplicates
   - Refresh tokens for security

4. **Composite Indexes**
   - Will be added based on query patterns that emerge during development

## Migration Management

1. **Naming Convention**
   ```
   YYYYMMDDHHMMSS_descriptive_name.py
   ```
   Example: `20240315123000_create_users_table.py`

2. **Migration History**
   - Initial migration: Create users table
   - Future migrations will be added as needed
   - Each migration must have `upgrade()` and `downgrade()` functions

3. **Backup Strategy**
   - Daily automated backups
   - Backup before each migration
   - Retention policy: 30 hari

## Schema Evolution Guidelines

1. **Backward Compatibility**
   - Avoid deleting columns that are still in use
   - Use nullable columns for adding new fields
   - Maintain existing indexes when making modifications

2. **Performance Considerations**
   - Monitor index size
   - Evaluate query performance after schema changes
   - Use EXPLAIN ANALYZE for optimization

3. **Security**
   - Encrypt sensitive data before storage
   - Audit trail for important data changes
   - Regular security review for access patterns

## Database Management

### Connection Pooling
```python
# Database connection pool configuration
POOL_MIN_SIZE = 5
POOL_MAX_SIZE = 20
POOL_MAX_OVERFLOW = 10
POOL_TIMEOUT = 30  # seconds
POOL_RECYCLE = 1800  # 30 minutes
```

### Backup Strategy
1. **Daily Backups**
   ```bash
   # Backup script (backup.sh)
   pg_dump -Fc meditrustal > /backups/meditrustal_$(date +%Y%m%d).dump
   ```
   - Retention: 7 daily backups
   - Time: 02:00 AM server time
   - Location: /backups/daily/

2. **Weekly Backups**
   - Retention: 4 weekly backups
   - Time: Sunday 03:00 AM
   - Location: /backups/weekly/

3. **Monthly Backups**
   - Retention: 12 monthly backups
   - Time: 1st day of month, 04:00 AM
   - Location: /backups/monthly/

### Monitoring Queries
1. **Performance Monitoring**
   ```sql
   -- Active queries monitoring
   SELECT pid, age(clock_timestamp(), query_start), usename, query, state
   FROM pg_stat_activity
   WHERE state != 'idle'
   AND query NOT ILIKE '%pg_stat_activity%'
   ORDER BY query_start desc;

   -- Table statistics
   SELECT schemaname, relname, seq_scan, seq_tup_read, 
          idx_scan, idx_tup_fetch, n_tup_ins, n_tup_upd, 
          n_tup_del, n_live_tup, n_dead_tup
   FROM pg_stat_user_tables
   ORDER BY n_live_tup DESC;

   -- Index usage
   SELECT schemaname, tablename, indexname, 
          idx_scan as number_of_scans,
          idx_tup_read as tuples_read,
          idx_tup_fetch as tuples_fetched
   FROM pg_stat_user_indexes
   ORDER BY number_of_scans DESC;
   ```

2. **Health Check Queries**
   ```sql
   -- Database size
   SELECT pg_size_pretty(pg_database_size('meditrustal_dev'));

   -- Table sizes
   SELECT relname as table_name,
          pg_size_pretty(pg_total_relation_size(relid)) as total_size
   FROM pg_catalog.pg_statio_user_tables
   ORDER BY pg_total_relation_size(relid) DESC;

   -- Connection count
   SELECT count(*) FROM pg_stat_activity;
   ```

3. **Alert Thresholds**
   - Database size > 80% capacity
   - Connection count > 80% max_connections
   - Query duration > 30 seconds
   - Dead tuple count > 10% of live tuples
   - Index usage < 5% for tables > 10,000 rows

### Maintenance Schedule
1. **VACUUM ANALYZE**
   - Automated: Daily at 03:00 AM
   - Manual: When dead tuples > 20%
   ```sql
   VACUUM (VERBOSE, ANALYZE) users;
   VACUUM (VERBOSE, ANALYZE) medical_records;
   VACUUM (VERBOSE, ANALYZE) sessions;
   ```

2. **Index Maintenance**
   - Weekly reindex of critical tables
   - Monthly index usage analysis
   ```sql
   REINDEX TABLE users;
   REINDEX TABLE medical_records;
   ```

3. **Statistics Update**
   ```sql
   ANALYZE users;
   ANALYZE medical_records;
   ANALYZE sessions;
   ```

## Audit Logging Schema

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id UUID NOT NULL REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID NOT NULL,
    old_value JSONB,
    new_value JSONB,
    ip_address INET NOT NULL,
    user_agent TEXT,
    request_id UUID NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    consent_reference UUID,
    retention_period INTERVAL NOT NULL,
    data_classification VARCHAR(50) NOT NULL,
    is_cross_border BOOLEAN DEFAULT FALSE,
    destination_country VARCHAR(100),
    encryption_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_event_time ON audit_logs(event_time);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_purpose ON audit_logs(purpose);

CREATE TABLE data_processing_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    purpose VARCHAR(100) NOT NULL,
    consent_given_at TIMESTAMP WITH TIME ZONE NOT NULL,
    consent_expires_at TIMESTAMP WITH TIME ZONE,
    consent_withdrawn_at TIMESTAMP WITH TIME ZONE,
    data_categories JSONB NOT NULL,
    processing_activities JSONB NOT NULL,
    third_parties JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_processing_consents_user ON data_processing_consents(user_id);
CREATE INDEX idx_data_processing_consents_purpose ON data_processing_consents(purpose);

CREATE TABLE data_deletion_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    request_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    requested_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    data_categories JSONB NOT NULL,
    verification_method VARCHAR(50) NOT NULL,
    verification_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_deletion_requests_user ON data_deletion_requests(user_id);
CREATE INDEX idx_data_deletion_requests_status ON data_deletion_requests(status);
```