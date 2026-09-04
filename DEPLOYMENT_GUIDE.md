# NUST Alumni Voting Portal - Deployment Guide

## Overview
This is a complete Azure Static Web App solution with Python Azure Functions backend and MongoDB for the NUST Alumni Association Elections platform.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Azure Static Web App (Frontend)                │
│  - React-based voting portal                            │
│  - Candidate profiles & live results dashboard          │
│  - Admin election management                            │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼──────────────┐        ┌────────▼────────────┐
│ Azure Functions      │        │  MongoDB Atlas      │
│ (Python Backend)     │◄─────►│  (Cloud Database)   │
│ - Election APIs      │        │  - Collections      │
│ - Vote Processing    │        │  - Vote Storage     │
│ - Results Query      │        │  - Voter Records    │
└──────────────────────┘        └─────────────────────┘
```

## Prerequisites

### Local Development
- Node.js 14+ and npm
- Python 3.9+
- Azure CLI
- Git

### Cloud Services
- Azure Account (with active subscription)
- MongoDB Atlas Account (free tier available)
- GitHub Account (for CI/CD)

## Step 1: Set Up MongoDB Atlas

### 1.1 Create MongoDB Atlas Cluster
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account or log in
3. Create a new project: "NUST Alumni Elections"
4. Click "Build a Cluster"
5. Select:
   - Cloud Provider: AWS
   - Region: Your preferred region (e.g., ap-southeast-1 for Asia)
   - Cluster Tier: M0 Shared (Free)
6. Click "Create Cluster"

### 1.2 Configure Network Access
1. In the Atlas dashboard, go to "Network Access"
2. Click "Add IP Address"
3. Select "Allow Access from Anywhere" (0.0.0.0/0) for development
4. For production, add specific Azure Function IP ranges
5. Click "Confirm"

### 1.3 Create Database User
1. Go to "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create username: `voting_admin`
5. Generate secure password (save this!)
6. Click "Add User"

### 1.4 Get Connection String
1. Click "Clusters"
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Select "Python" and version 3.9+
5. Copy the connection string
6. Format: `mongodb+srv://voting_admin:PASSWORD@cluster.mongodb.net/voting_portal?retryWrites=true&w=majority`

## Step 2: Local Development Setup

### 2.1 Clone and Install Dependencies
```bash
# Clone the repository
git clone <your-repo-url>
cd voting-portal

# Install backend dependencies
pip install -r api/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2.2 Configure Environment Variables
```bash
# Create .env file in project root
cp .env.example .env

# Edit .env with your values:
MONGODB_CONNECTION_STRING=your-mongodb-connection-string
JWT_SECRET=your-secret-key-here
REACT_APP_API_URL=http://localhost:7071/api
```

### 2.3 Run Locally
```bash
# Terminal 1: Start backend (Azure Functions emulator)
cd api
func start

# Terminal 2: Start frontend
cd frontend
npm start
```

## Step 3: Deploy to Azure

### 3.1 Create Azure Resources

```bash
# Set variables
RESOURCE_GROUP="nust-alumni-rg"
LOCATION="eastasia"
FUNCTION_APP_NAME="nust-voting-api"
STORAGE_ACCOUNT="nustalumnistorage"

# Login to Azure
az login

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create storage account for Functions
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name $FUNCTION_APP_NAME \
  --storage-account $STORAGE_ACCOUNT \
  --os-type Linux
```

### 3.2 Configure Function App Settings
```bash
# Add MongoDB connection string
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    MONGODB_CONNECTION_STRING="your-mongodb-connection-string" \
    JWT_SECRET="your-secret-key"

# Enable CORS for frontend
az functionapp cors add \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP_NAME \
  --allowed-origins "*"
```

### 3.3 Create Static Web App
```bash
# Create Azure Static Web App
az staticwebapp create \
  --name nust-voting-portal \
  --resource-group $RESOURCE_GROUP \
  --location eastasia \
  --source https://github.com/your-username/voting-portal \
  --branch main \
  --app-location "frontend" \
  --output-location "build" \
  --api-location "api"
```

### 3.4 Get API URL
```bash
# Get the API URL from Azure
FUNCTION_URL=$(az functionapp show \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "defaultHostName" -o tsv)

echo "API URL: https://$FUNCTION_URL"
```

### 3.5 Update Frontend Configuration
```bash
# Update environment variables in Static Web App
az staticwebapp appsettings set \
  --name nust-voting-portal \
  --setting-names REACT_APP_API_URL="https://$FUNCTION_URL/api"
```

## Step 4: GitHub Actions CI/CD Setup

The Azure Static Web App automatically creates a GitHub Actions workflow. Update it:

### 4.1 Workflow File Location
File: `.github/workflows/azure-static-web-apps-*.yml`

### 4.2 Update Workflow
```yaml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      
      - name: Install frontend dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Build frontend
        working-directory: ./frontend
        run: npm run build
        env:
          REACT_APP_API_URL: ${{ secrets.API_URL }}
      
      - name: Deploy to Azure Static Web Apps
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "frontend/build"
          api_location: "api"
          output_location: "build"
```

## Step 5: Database Initialization

### 5.1 Create Collections
```python
# Run this script to initialize MongoDB collections
python scripts/init_database.py
```

### 5.2 Add Sample Admin User
```python
# Create admin user
python scripts/seed_admin.py --email admin@nustalumni.org --password admin123
```

## API Endpoints

### Elections
- `GET /api/elections` - Get all elections
- `GET /api/elections/{id}` - Get election details
- `POST /api/elections` - Create election (admin)
- `PUT /api/elections/{id}` - Update election (admin)
- `POST /api/elections/{id}/activate` - Activate election (admin)
- `POST /api/elections/{id}/close` - Close election (admin)

### Candidates
- `GET /api/elections/{id}/candidates` - Get candidates
- `POST /api/elections/{id}/candidates` - Add candidate (admin)
- `GET /api/elections/{id}/candidates?position=President` - Filter by position

### Voting
- `POST /api/elections/{id}/vote` - Cast vote
- `GET /api/elections/{id}/results` - Get live results
- `GET /api/elections/{id}/results/{position}` - Get position results

## Key Features

### For Voters
✅ View all elections and candidate profiles
✅ See candidate bios, platforms, and details
✅ Real-time live election results dashboard
✅ Vote tracking (one vote per election)
✅ Multiple positions per election

### For Admins
✅ Create and manage elections
✅ Add candidates with detailed profiles
✅ Activate/close elections
✅ View live voting statistics
✅ Voter turnout tracking

### For Election Management
✅ Configurable number of seats (default: 10)
✅ Multiple positions per election
✅ Vote validation (prevent duplicate votes)
✅ Real-time vote counting
✅ Voter registration tracking
✅ Turnout percentage calculation

## Security Features

1. **JWT Authentication** - Secure token-based authentication
2. **MongoDB Encryption** - Data at rest encryption
3. **HTTPS/TLS** - All communication encrypted
4. **CORS** - Restricted cross-origin requests
5. **Input Validation** - Server-side validation on all inputs
6. **Role-Based Access** - Admin vs. voter permissions

## Monitoring and Logging

### Azure Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --app nust-voting-api \
  --resource-group $RESOURCE_GROUP \
  --location eastasia
```

### View Logs
```bash
# View Function App logs
az functionapp log tail \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

## Scaling Configuration

### Auto-Scaling (Azure Functions)
- Automatic scaling based on demand
- Pay per execution (Consumption plan)
- No charges when idle

### Database Performance
- MongoDB Atlas auto-scaling available
- Add read replicas for high load
- Use connection pooling in Functions

## Troubleshooting

### Common Issues

**1. CORS Errors**
```bash
# Enable CORS for all origins (development only)
az functionapp cors add --resource-group $RESOURCE_GROUP --name $FUNCTION_APP_NAME --allowed-origins "*"
```

**2. MongoDB Connection Failed**
- Check connection string in .env
- Verify IP address is whitelisted in Atlas
- Ensure credentials are correct

**3. Frontend Can't Reach API**
- Verify API URL in REACT_APP_API_URL
- Check CORS settings on Function App
- Ensure Function App is running

**4. Vote Not Recording**
- Check MongoDB connection
- Verify voter hasn't already voted
- Check vote endpoint authorization

## Maintenance

### Backup MongoDB
```bash
# Enable automatic backups in MongoDB Atlas
# - Go to Backup in Atlas dashboard
- Set backup frequency to daily
- Retention period: 35 days (default)
```

### Monitor Costs
- Azure Functions: ~$0.2/million executions
- MongoDB Atlas Free Tier: Up to 512MB storage
- Static Web App: Free tier for development

## Next Steps

1. ✅ Deploy to Azure
2. ✅ Test all voting workflows
3. ✅ Configure email notifications (optional)
4. ✅ Add voter registration
5. ✅ Set up election reminders
6. ✅ Create audit logs

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review MongoDB and Azure documentation
3. Check Function App logs in Azure Portal

---

**Version**: 1.0  
**Last Updated**: 2024  
**Framework**: React, Python, MongoDB, Azure
