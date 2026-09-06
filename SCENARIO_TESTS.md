# Agorapulse Connector — Scenario & Verification Tests

## Plausible Scenario Testing (PST) & Part D Checks

### D1: Deploy & Manifest Verification
- Manifest validated against Imperal SDK v5.13.1 schema.
- Tools declared: connect_agorapulse, list_connections, disconnect_agorapulse, list_profiles, list_posts, create_post, delete_post, list_inbox, audit_social_health.
- UI panels: left sidebar (agorapulse_sidebar) and settings modal (__agorapulse_settings).

### D2: Idempotency & Re-entrancy
- Multiple list operations return deterministic collections.
- Disconnect securely deletes connection credentials without residual secret leakage.

### D3: Security, SSRF & Credential Masking
- BYOC model: OAuth 2.0 access tokens stored in encrypted Imperal Secret Store.
- Access token masked (`agora_...`) in all returned connection records and logs.
- Strict HTTPS base URL validation against `https://api.agorapulse.com/v1`.

### D4: Regression Grep
- Zero residue of legacy C30 email marketing models (`Subscriber`, `Campaign`, `AuditAudienceHealth`).
