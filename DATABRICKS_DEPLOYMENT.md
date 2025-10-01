# Databricks App Deployment Guide

This guide explains how to deploy the Genie to Chart POC as a Databricks App using the native Databricks Apps platform.

## Prerequisites

1. **Databricks Workspace** with Apps enabled
2. **Genie Space** configured in your workspace
3. **Azure OpenAI** service with deployed model
4. **Databricks CLI** installed and configured

## Deployment Steps

### 1. Prepare Secrets

Create the following secrets in your Databricks workspace to securely store credentials:

```bash
# Create secret scope (if not exists)
databricks secrets create-scope genie-chart-app

# Add Databricks configuration
databricks secrets put-secret genie-chart-app databricks-host-secret
databricks secrets put-secret genie-chart-app databricks-token-secret
databricks secrets put-secret genie-chart-app genie-space-id-secret

# Add Azure OpenAI configuration
databricks secrets put-secret genie-chart-app azure-openai-endpoint-secret
databricks secrets put-secret genie-chart-app azure-openai-key-secret
databricks secrets put-secret genie-chart-app azure-openai-deployment-secret
```

### 2. Update app.yaml Configuration

The `app.yaml` file is already configured to reference these secrets. Update the secret names if you use different ones:

```yaml
env:
  - name: 'GENIE_DATABRICKS_HOST'
    valueFrom: 'databricks-host-secret'
  - name: 'GENIE_DATABRICKS_TOKEN'
    valueFrom: 'databricks-token-secret'
  # ... other secrets
```

### 3. Deploy the App

#### Option A: Using Databricks CLI

```bash
# Navigate to project directory
cd "/path/to/genie to chart poc"

# Deploy the app
databricks apps deploy genie-chart-app --source-path .
```

#### Option B: Using Databricks Workspace UI

1. Open your Databricks workspace
2. Navigate to **Apps** in the sidebar
3. Click **Create App**
4. Upload the project files or connect to your Git repository
5. Configure the app settings using the `app.yaml` configuration

### 4. Configure App Settings

The app will run with the following configuration:

- **Runtime**: Flask development server (production mode in Databricks)
- **Port**: 8080 (Databricks standard)
- **Debug Mode**: Disabled in Databricks environment
- **Host**: 0.0.0.0 (accepts connections from all interfaces)

### 5. Access the App

Once deployed, the app will be available at:
```
https://<workspace-url>/apps/<app-name>
```

## Environment Variables

The app uses the following environment variables (configured in `app.yaml`):

### Required Secrets
- `GENIE_DATABRICKS_HOST`: Your Databricks workspace URL
- `GENIE_DATABRICKS_TOKEN`: Personal access token or service principal token
- `GENIE_SPACE_ID`: ID of your Genie space
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI service endpoint
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT`: Name of your deployed model

### Optional Configuration
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-06-01)
- `MAX_QUEUE_WORKERS`: Number of message processing workers (default: 2)
- `MAX_QUEUE_SIZE`: Maximum queue size (default: 50)
- `LOG_LEVEL`: Logging level (default: INFO)

## Security Considerations

1. **Use Secrets**: All sensitive credentials are stored in Databricks secrets
2. **Service Principal**: Consider using a service principal instead of personal tokens
3. **Network Security**: The app runs within Databricks' secure environment
4. **Access Control**: Use Databricks workspace permissions to control app access

## Monitoring and Troubleshooting

### View App Logs
```bash
databricks apps logs genie-chart-app
```

### Check App Status
```bash
databricks apps list
databricks apps get genie-chart-app
```

### Common Issues

1. **Secret Access**: Ensure the app has permission to access the secret scope
2. **Genie Space**: Verify the Genie space ID is correct and accessible
3. **Azure OpenAI**: Check that the deployment name and endpoint are correct
4. **Memory**: Monitor memory usage; increase workers if needed

## Scaling Considerations

- **Concurrency**: Flask handles requests sequentially; consider multiple app instances for high load
- **Memory**: Monitor memory usage through Databricks monitoring
- **Queue Size**: Adjust `MAX_QUEUE_SIZE` based on expected load
- **Threading**: The app uses background threads for message processing

## Development vs Production

### Development
- Use personal access tokens
- Debug mode enabled (port 5000)
- Detailed logging enabled

### Production (Databricks Apps)
- Use service principal authentication via secrets
- Production mode (port 8080, debug disabled)
- INFO or WARNING log level
- Built-in Databricks monitoring

## Benefits of Databricks App Deployment

1. **Native Integration**: Direct access to Databricks APIs without external authentication
2. **Scalability**: Automatic scaling within Databricks infrastructure
3. **Security**: Secure secret management and network isolation
4. **Monitoring**: Built-in logging and monitoring capabilities
5. **Cost Efficiency**: Pay only for compute resources used
6. **Maintenance**: Automatic updates and patches from Databricks

## Next Steps

1. Deploy the app using the steps above
2. Test functionality with sample queries
3. Configure monitoring and alerting
4. Set up CI/CD pipeline for updates
5. Scale based on usage patterns

For more information, see the [Databricks Apps documentation](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/app-runtime).
