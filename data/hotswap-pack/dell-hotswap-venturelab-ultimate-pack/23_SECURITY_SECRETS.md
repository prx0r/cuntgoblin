# Secrets / Security

## HotSwap must never become a credential vault

Store secrets in:
- LiteLLM-supported secret/env management
- Hermes .env/auth where needed
- dedicated secret manager if later deployed

HotSwap stores opaque refs.

## Logs

Redact:
- API keys
- auth headers
- OAuth tokens
- provider credentials

## Account discovery

Dell may record activation requirements, but not secrets.

## Multi-user future

Use LiteLLM virtual keys/team budgets instead of reinventing auth/spend enforcement.

## Reproducibility

Execution plans may record:
`credential_ref=litellm:model_deployment_17`

not the credential value.
