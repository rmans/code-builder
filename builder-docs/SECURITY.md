# Security Policy

## Overview

This document outlines security practices and policies for the Code Builder project, with particular emphasis on protecting Personally Identifiable Information (PII) and sensitive data in discovery contexts and generated artifacts.

## PII Protection in Discovery Contexts

### What is PII?

Personally Identifiable Information (PII) includes any data that can be used to identify, contact, or locate an individual. In the context of code analysis and discovery, this includes:

- **Email addresses** (e.g., `user@example.com`, `john.doe@company.com`)
- **Names** (e.g., `John Doe`, `Jane Smith`)
- **Phone numbers** (e.g., `+1-555-123-4567`, `(555) 123-4567`)
- **Addresses** (e.g., `123 Main St, City, State 12345`)
- **Social Security Numbers** (e.g., `123-45-6789`)
- **Credit card numbers** (e.g., `4111-1111-1111-1111`)
- **API keys and tokens** (e.g., `sk-1234567890abcdef`, `Bearer eyJhbGciOiJIUzI1NiIs...`)
- **Database connection strings** (e.g., `postgresql://user:pass@host:port/db`)
- **Private keys** (e.g., `-----BEGIN PRIVATE KEY-----`)
- **Passwords and secrets** (e.g., `password123`, `secret_key_here`)

### Discovery Context PII Risks

When running discovery analysis on codebases, the following artifacts may contain PII:

- **`discovery_context.yml`** - Generated discovery context files
- **`pack_context.json`** - Context packs for AI code generation
- **`context.md`** - Human-readable context files
- **Discovery outputs** - Generated reports and analysis files
- **CI/CD artifacts** - Uploaded discovery and context artifacts

### PII Detection and Redaction

The Code Builder includes automated PII detection and optional redaction capabilities:

#### Detection Patterns

The system automatically detects the following PII patterns:

```yaml
# Email addresses
email_patterns:
  - "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
  - "[a-zA-Z0-9._%+-]+\+[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Phone numbers
phone_patterns:
  - "\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"
  - "\+?[0-9]{1,3}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}"

# API keys and tokens
api_key_patterns:
  - "sk-[a-zA-Z0-9]{20,}"
  - "pk_[a-zA-Z0-9]{20,}"
  - "Bearer [a-zA-Z0-9._-]+"
  - "Basic [a-zA-Z0-9+/=]+"

# Database connection strings
db_patterns:
  - "postgresql://[^:]+:[^@]+@[^/]+/[^\\s]+"
  - "mysql://[^:]+:[^@]+@[^/]+/[^\\s]+"
  - "mongodb://[^:]+:[^@]+@[^/]+/[^\\s]+"

# Credit card numbers
cc_patterns:
  - "[0-9]{4}[-\\s]?[0-9]{4}[-\\s]?[0-9]{4}[-\\s]?[0-9]{4}"
  - "[0-9]{13,19}"

# Social Security Numbers
ssn_patterns:
  - "[0-9]{3}-[0-9]{2}-[0-9]{4}"
  - "[0-9]{9}"

# Private keys
private_key_patterns:
  - "-----BEGIN PRIVATE KEY-----"
  - "-----BEGIN RSA PRIVATE KEY-----"
  - "-----BEGIN EC PRIVATE KEY-----"
```

#### Redaction Options

When PII is detected, the system provides several redaction options:

1. **Full Redaction**: Replace with `[REDACTED]`
2. **Partial Redaction**: Replace with `[REDACTED-EMAIL]`, `[REDACTED-PHONE]`, etc.
3. **Hash Redaction**: Replace with SHA-256 hash for tracking
4. **Pattern Redaction**: Replace with pattern description (e.g., `[EMAIL-PATTERN]`)

#### Usage

```bash
# Run discovery with PII detection and warnings
python builder/cli.py discover:scan --auto-generate

# Run discovery with PII redaction
python builder/cli.py discover:scan --auto-generate --redact-pii

# Check for PII in existing discovery context
python builder/cli.py discover:validate --check-pii

# Redact PII from existing context
python builder/cli.py discover:redact --input discovery_context.yml --output discovery_context_redacted.yml
```

## Security Best Practices

### For Developers

1. **Pre-commit Checks**: Run PII detection before committing discovery contexts
2. **Environment Variables**: Use environment variables for sensitive configuration
3. **Secrets Management**: Never hardcode API keys, passwords, or tokens
4. **Code Review**: Review discovery contexts for PII before sharing
5. **Access Control**: Limit access to discovery artifacts containing sensitive data

### For CI/CD

1. **Artifact Scanning**: Scan uploaded artifacts for PII before making them public
2. **Access Logging**: Log access to discovery artifacts
3. **Retention Policies**: Implement appropriate retention policies for sensitive artifacts
4. **Redaction Pipeline**: Automatically redact PII in CI/CD artifacts

### For Code Analysis

1. **Scope Limitation**: Limit discovery analysis to necessary files only
2. **Pattern Exclusion**: Exclude files containing sensitive data from analysis
3. **Context Filtering**: Filter out sensitive information from generated contexts
4. **Audit Trails**: Maintain audit trails of PII detection and redaction

## Configuration

### PII Detection Configuration

Create a `.pii-config.yml` file in your project root:

```yaml
# PII Detection Configuration
pii_detection:
  enabled: true
  strict_mode: false  # Enable for production
  
  # Detection patterns
  patterns:
    email: true
    phone: true
    api_keys: true
    db_connections: true
    credit_cards: true
    ssn: true
    private_keys: true
  
  # Redaction settings
  redaction:
    mode: "partial"  # full, partial, hash, pattern
    preserve_format: true  # Keep original format structure
    
  # Exclusions
  exclusions:
    files:
      - "**/node_modules/**"
      - "**/.git/**"
      - "**/dist/**"
      - "**/build/**"
    patterns:
      - "test@example.com"  # Known test emails
      - "555-123-4567"      # Known test phone numbers
```

### Discovery Context Security

When generating discovery contexts:

1. **Review Before Generation**: Check source files for sensitive data
2. **Use Redaction**: Enable PII redaction for sensitive codebases
3. **Limit Scope**: Only analyze necessary files and directories
4. **Secure Storage**: Store discovery contexts securely
5. **Access Control**: Implement appropriate access controls

## Incident Response

### PII Exposure Incident

If PII is accidentally exposed in discovery contexts:

1. **Immediate Response**:
   - Remove or redact the exposed data immediately
   - Revoke any shared access to the artifacts
   - Notify relevant stakeholders

2. **Assessment**:
   - Determine scope of exposure
   - Identify affected individuals
   - Assess potential impact

3. **Remediation**:
   - Redact or remove PII from all copies
   - Update security procedures
   - Implement additional safeguards

4. **Notification**:
   - Notify affected individuals if required
   - Report to relevant authorities if necessary
   - Document the incident

## Compliance

### GDPR Compliance

For European Union data protection:

- **Data Minimization**: Only collect necessary data for discovery
- **Purpose Limitation**: Use discovery data only for intended purposes
- **Storage Limitation**: Implement appropriate retention policies
- **Right to Erasure**: Provide mechanisms to remove PII from discovery contexts

### CCPA Compliance

For California Consumer Privacy Act:

- **Transparency**: Clearly document PII collection and use
- **Consumer Rights**: Provide mechanisms for data access and deletion
- **Opt-out**: Allow consumers to opt out of data collection
- **Data Security**: Implement reasonable security measures

## Tools and Resources

### PII Detection Tools

- **Built-in Scanner**: `python builder/cli.py discover:validate --check-pii`
- **Redaction Tool**: `python builder/cli.py discover:redact`
- **Pattern Testing**: `python builder/cli.py discover:test-patterns`

### External Tools

- **GitLeaks**: Detect secrets in Git repositories
- **TruffleHog**: Find secrets in code and configuration
- **GitGuardian**: Monitor for secrets in real-time
- **Detect-secrets**: Pre-commit hook for secret detection

### Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [GDPR Guidelines](https://gdpr.eu/)
- [CCPA Compliance Guide](https://oag.ca.gov/privacy/ccpa)

## Contact

For security concerns or questions about PII handling:

- **Security Team**: security@example.com
- **Privacy Officer**: privacy@example.com
- **Incident Response**: security-incident@example.com

## Changelog

- **2025-09-06**: Initial security policy with PII protection guidelines
- **2025-09-06**: Added PII detection patterns and redaction capabilities
- **2025-09-06**: Implemented discovery context security measures
