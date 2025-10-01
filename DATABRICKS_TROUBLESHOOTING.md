# Databricks Apps Troubleshooting Guide

This guide helps resolve common issues when deploying the Genie to Chart POC as a Databricks App.

## Common Import Errors

### DatabricksError Import Issue

**Error:**
```
ImportError: cannot import name 'DatabricksError' from 'databricks.sdk.errors'
```

**Solution:**
This has been fixed in the latest version with a compatibility layer. The app now handles different SDK versions automatically.

**What was changed:**
- Added `backend/utils/databricks_compat.py` compatibility layer
- Flexible error handling that works across SDK versions
- Graceful fallback to generic exceptions if needed

### SDK Version Compatibility

**Issue:** Different Databricks environments may have different SDK versions.

**Solution:** The app now uses version-flexible imports:
```python
# Tries multiple import paths automatically
from backend.utils.databricks_compat import DatabricksError
```

## Environment Configuration Issues

### Missing Environment Variables

**Error:**
```
[ERROR] Could not start app. app crashed unexpectedly.
ValidationError: Field required [type=missing, input={...}]
```

**Solution:**
1. Ensure all required secrets are created in Databricks:
```bash
databricks secrets create-scope genie-chart-app
databricks secrets put-secret genie-chart-app azure-openai-endpoint-secret
databricks secrets put-secret genie-chart-app azure-openai-key-secret
databricks secrets put-secret genie-chart-app azure-openai-deployment-secret
```

2. Verify `app.yaml` references the correct secret names:
```yaml
env:
  - name: 'GENIE_DATABRICKS_HOST'
    valueFrom: 'databricks-host-secret'
  - name: 'AZURE_OPENAI_ENDPOINT'
    valueFrom: 'azure-openai-endpoint-secret'
```

### Authentication Issues

**Error:**
```
[ERROR] Failed to initialize GenieClient: [PERMISSION_DENIED] Access denied
```

**Solutions:**
1. **For Development:** Use personal access token in secrets
2. **For Production:** Use service principal:
```bash
databricks secrets put-secret genie-chart-app databricks-token-secret
# Enter service principal token when prompted
```

## Runtime Issues

### Port Binding Problems

**Error:**
```
[ERROR] Address already in use
```

**Solution:**
The app automatically detects Databricks environment and uses port 8080. No manual configuration needed.

### Memory Issues

**Error:**
```
[ERROR] Out of memory
```

**Solutions:**
1. Reduce `MAX_QUEUE_WORKERS` in `app.yaml`:
```yaml
env:
  - name: 'MAX_QUEUE_WORKERS'
    value: '1'  # Reduce from 2 to 1
```

2. Reduce `MAX_QUEUE_SIZE`:
```yaml
env:
  - name: 'MAX_QUEUE_SIZE'
    value: '25'  # Reduce from 50 to 25
```

## Genie Integration Issues

### Space ID Problems

**Error:**
```
[ERROR] No Genie spaces found
```

**Solutions:**
1. Verify Genie is enabled in your workspace
2. Check space ID in secrets:
```bash
databricks secrets get-secret genie-chart-app genie-space-id-secret
```

3. List available spaces:
```python
from databricks.sdk import WorkspaceClient
client = WorkspaceClient()
spaces = client.genie.list_spaces()
print([space.space_id for space in spaces.spaces])
```

### Query Failures

**Error:**
```
[ERROR] Failed to query Genie: [INVALID_REQUEST]
```

**Solutions:**
1. Check if the Genie space has proper data sources configured
2. Verify the space is accessible with your authentication
3. Test with a simple query first

## Azure OpenAI Issues

### Deployment Not Found

**Error:**
```
[ERROR] The API deployment for this resource does not exist
```

**Solutions:**
1. Verify deployment name in Azure OpenAI Studio
2. Update secret with correct deployment name:
```bash
databricks secrets put-secret genie-chart-app azure-openai-deployment-secret
# Enter correct deployment name (e.g., gpt-4o, not gpt-5)
```

### Rate Limiting

**Error:**
```
[ERROR] Rate limit exceeded
```

**Solution:**
The app has built-in exponential backoff. If issues persist:
1. Increase retry settings in `app.yaml`:
```yaml
env:
  - name: 'MAX_RETRIES'
    value: '10'  # Increase from 5
  - name: 'MAX_BACKOFF'
    value: '120.0'  # Increase from 60.0
```

## Debugging Steps

### 1. Check App Logs
```bash
databricks apps logs genie-chart-app
```

### 2. Verify Secrets
```bash
databricks secrets list-secrets genie-chart-app
```

### 3. Test Configuration
Run the test script locally:
```bash
python test_databricks_config.py
```

### 4. Check App Status
```bash
databricks apps get genie-chart-app
```

## Performance Optimization

### For High Load
1. **Increase workers:**
```yaml
env:
  - name: 'MAX_QUEUE_WORKERS'
    value: '4'
```

2. **Optimize timeouts:**
```yaml
env:
  - name: 'INITIAL_BACKOFF'
    value: '0.5'  # Faster initial retry
```

### For Low Memory
1. **Reduce concurrency:**
```yaml
env:
  - name: 'MAX_QUEUE_WORKERS'
    value: '1'
  - name: 'MAX_QUEUE_SIZE'
    value: '10'
```

## Getting Help

1. **Check logs first:** `databricks apps logs genie-chart-app`
2. **Test locally:** Run `python test_databricks_config.py`
3. **Verify secrets:** Ensure all required secrets are set correctly
4. **Check permissions:** Verify workspace and Genie access
5. **Monitor resources:** Watch memory and CPU usage in Databricks

## Common Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Import errors | Use latest version with compatibility layer |
| Missing secrets | Create all required secrets in Databricks |
| Port conflicts | App auto-detects environment (no action needed) |
| Memory issues | Reduce `MAX_QUEUE_WORKERS` to 1 |
| Genie access | Verify space ID and permissions |
| Azure OpenAI | Check deployment name and endpoint |
| Rate limits | Built-in backoff (increase `MAX_RETRIES` if needed) |

The app is designed to be robust and handle most common issues automatically. Most problems are related to configuration rather than code issues.
