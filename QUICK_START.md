# NUST Alumni Voting Portal - Quick Start Commands

## 🚀 One-Command Setup (Local)

```bash
# Clone and setup
git clone <repo-url> && cd voting-portal

# Install everything
pip install -r api/requirements.txt && cd frontend && npm install && cd ..

# Copy environment
cp .env.example .env

# Edit .env with your MongoDB connection string
# Then run:

# Terminal 1: Backend
cd api && func start

# Terminal 2: Frontend  
cd frontend && npm start
```

## 🔧 Essential Development Commands

### Setup
```bash
# Initialize MongoDB collections
python scripts/init_database.py

# Create admin user
python scripts/seed_admin.py --email admin@nustalumni.org --password admin123

# Add sample data
python scripts/seed_sample_data.py
```

### Local Development
```bash
# Start backend (Azure Functions emulator)
cd api && func start

# Start frontend (React dev server)
cd frontend && npm start

# Run tests (if configured)
python -m pytest api/tests/
npm test --prefix frontend
```

### Build
```bash
# Build frontend for production
cd frontend && npm run build

# Output goes to: frontend/build/
```

## ☁️ Azure Deployment Commands

### Initial Setup
```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create resource group
az group create --name nust-alumni-rg --location eastasia

# Create storage account
az storage account create \
  --name nustalumnistorage \
  --resource-group nust-alumni-rg \
  --location eastasia \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group nust-alumni-rg \
  --consumption-plan-location eastasia \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name nust-voting-api \
  --storage-account nustalumnistorage \
  --os-type Linux

# Create Static Web App
az staticwebapp create \
  --name nust-voting-portal \
  --resource-group nust-alumni-rg \
  --location eastasia \
  --source https://github.com/YOUR_USERNAME/voting-portal \
  --branch main \
  --app-location "frontend" \
  --output-location "build" \
  --api-location "api"
```

### Configuration
```bash
# Set environment variables for Function App
az functionapp config appsettings set \
  --name nust-voting-api \
  --resource-group nust-alumni-rg \
  --settings \
    MONGODB_CONNECTION_STRING="your-connection-string" \
    JWT_SECRET="your-secret-key"

# Enable CORS
az functionapp cors add \
  --resource-group nust-alumni-rg \
  --name nust-voting-api \
  --allowed-origins "*"

# Get Function App URL
az functionapp show \
  --name nust-voting-api \
  --resource-group nust-alumni-rg \
  --query "defaultHostName" -o tsv
```

### Deployment
```bash
# Deploy backend (from api directory)
cd api && func azure functionapp publish nust-voting-api

# Deploy frontend (automatic with GitHub Actions)
# Just push to main branch:
git push origin main

# Or manual deployment:
cd frontend && npm run build
az staticwebapp update \
  --name nust-voting-portal \
  --resource-group nust-alumni-rg \
  --app-location "build"
```

### Monitoring
```bash
# View Function App logs
az functionapp log tail \
  --name nust-voting-api \
  --resource-group nust-alumni-rg

# Check resource group costs
az costmanagement query --time-period P30D --resource-group nust-alumni-rg

# Get deployment status
az staticwebapp show \
  --name nust-voting-portal \
  --resource-group nust-alumni-rg
```

### Cleanup (if needed)
```bash
# Delete everything in resource group
az group delete --name nust-alumni-rg --yes

# Or delete specific resources
az functionapp delete --name nust-voting-api --resource-group nust-alumni-rg
az staticwebapp delete --name nust-voting-portal --resource-group nust-alumni-rg
```

## 📊 MongoDB Commands

### Connect Directly
```bash
# Using MongoDB CLI
mongosh "your-connection-string"

# List databases
show databases

# Use voting portal database
use voting_portal

# See collections
show collections

# Query elections
db.elections.find()

# Count votes for an election
db.votes.countDocuments({ election_id: "ELECTION_ID" })

# Get voting stats
db.votes.aggregate([
  { $group: { _id: "$candidate_id", votes: { $sum: 1 } } },
  { $sort: { votes: -1 } }
])
```

## 🌐 API Test Commands

### Using cURL

```bash
# Get all elections
curl https://your-api.azurewebsites.net/api/elections

# Create election (requires admin token)
curl -X POST https://your-api.azurewebsites.net/api/elections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "2024 Elections",
    "description": "Annual alumni elections",
    "total_seats": 10
  }'

# Get candidates
curl https://your-api.azurewebsites.net/api/elections/{electionId}/candidates

# Cast vote (requires user token)
curl -X POST https://your-api.azurewebsites.net/api/elections/{electionId}/vote \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"candidate_id": "CANDIDATE_ID"}'

# Get results
curl https://your-api.azurewebsites.net/api/elections/{electionId}/results
```

### Using PowerShell

```powershell
# Get elections
Invoke-RestMethod -Uri "https://your-api.azurewebsites.net/api/elections" -Method Get

# Create election
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = @{
    title = "2024 Elections"
    description = "Annual alumni elections"
    total_seats = 10
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://your-api.azurewebsites.net/api/elections" `
  -Method Post -Headers $headers -Body $body
```

## 🐛 Debugging

### Check Backend Logs
```bash
# View real-time logs
az functionapp log tail --name nust-voting-api --resource-group nust-alumni-rg

# Or use func cli
cd api && func azure functionapp fetch-app-settings nust-voting-api
```

### Test MongoDB Connection
```python
# Quick test script
from pymongo import MongoClient
import os

try:
    client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
    client.server_info()
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
```

### Check Frontend Build
```bash
cd frontend
npm run build

# Check output
ls -la build/
```

## 📦 Environment Variables Reference

```bash
# Backend (.env file)
MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/voting_portal
JWT_SECRET=your-secret-key-here
API_URL=https://your-api.azurewebsites.net/api

# Frontend (set in Static Web App)
REACT_APP_API_URL=https://your-api.azurewebsites.net/api
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# File: .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: cd frontend && npm install && npm run build
      - uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_TOKEN }}
```

## 📋 Checklist for Going Live

- [ ] MongoDB Atlas cluster created
- [ ] Connection string saved in .env
- [ ] Local testing complete (elections, candidates, voting)
- [ ] Azure resources created
- [ ] Environment variables set in Azure
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] CORS configured
- [ ] Custom domain configured (optional)
- [ ] SSL certificate installed (automatic with Azure)
- [ ] Database backups enabled
- [ ] Monitoring alerts configured
- [ ] Team trained on admin interface
- [ ] First election created as test
- [ ] Sample candidates added
- [ ] Admin user created
- [ ] Voter data prepared (if needed)
- [ ] Email templates ready (if using notifications)

## 🆘 Emergency Commands

### Roll back deployment
```bash
# Get previous deployment ID
az staticwebapp list --resource-group nust-alumni-rg

# Redeploy previous version
git revert HEAD
git push origin main
```

### Reset database (⚠️ DATA LOSS)
```bash
# Connect to MongoDB
mongosh "your-connection-string"

# Drop database
db.dropDatabase()

# Reinitialize
exit
python scripts/init_database.py
```

### Clear Function App cache
```bash
az functionapp config appsettings delete \
  --name nust-voting-api \
  --resource-group nust-alumni-rg \
  --setting-names SOME_CACHE_KEY
```

## 📞 Useful Links

- Azure Portal: https://portal.azure.com
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
- GitHub Actions: https://github.com/YOUR_USERNAME/voting-portal/actions
- Function App Dashboard: https://portal.azure.com → Function App → nust-voting-api
- Static Web App Dashboard: https://portal.azure.com → Static Web App → nust-voting-portal

## 💡 Pro Tips

1. **Local Testing**: Always test locally before deploying
2. **Secrets**: Never commit .env file with real credentials
3. **Backups**: Enable MongoDB backups before going live
4. **Monitoring**: Set up Azure Alerts for function failures
5. **Logging**: Check logs first when debugging issues
6. **Testing**: Use Postman to test API endpoints
7. **Performance**: Monitor cold starts in Azure Portal

---

**Need Help?** Check README.md and DEPLOYMENT_GUIDE.md for detailed information.
