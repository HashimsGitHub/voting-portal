# NUST Alumni Voting Portal

A modern, secure, and scalable election platform for NUST Alumni Association built with Azure, Python, React, and MongoDB.

## 🎯 Features

### Core Functionality
- **Election Management**: Create multiple elections with configurable seats (default: 10)
- **Candidate Profiles**: Detailed candidate information including bio, platform, and contact
- **Live Voting**: Real-time voting with duplicate prevention
- **Live Results**: Real-time results dashboard with vote counting and turnout tracking
- **Admin Dashboard**: Complete election management interface

### Technical Features
- **Serverless Backend**: Python Azure Functions (automatic scaling)
- **MongoDB Integration**: NoSQL database for flexible data storage
- **Real-time Updates**: Live results refresh every 5 seconds
- **JWT Authentication**: Secure token-based authentication
- **Responsive Design**: Mobile-friendly React frontend
- **Azure Static Web Apps**: Automatic CI/CD deployment

## 🚀 Quick Start

### Local Development

1. **Clone Repository**
```bash
git clone <repository-url>
cd voting-portal
```

2. **Set Up Environment**
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string
```

3. **Install Dependencies**
```bash
# Backend
pip install -r api/requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

4. **Run Locally**
```bash
# Terminal 1: Backend
cd api
func start

# Terminal 2: Frontend
cd frontend
npm start
```

Visit `http://localhost:3000` in your browser.

## 📋 Project Structure

```
voting-portal/
├── api/
│   ├── models/
│   │   └── election.py          # Data models
│   ├── repositories/
│   │   └── election_repository.py # Database operations
│   ├── services/
│   │   └── election_service.py  # Business logic
│   ├── function_app_voting.py   # Azure Functions endpoints
│   ├── requirements.txt
│   └── host.json
├── frontend/
│   ├── src/
│   │   ├── pages/              # React page components
│   │   ├── components/         # Reusable components
│   │   ├── services/           # API service
│   │   ├── styles/             # CSS files
│   │   └── App.jsx
│   ├── package.json
│   └── public/
├── staticwebapp.config.json     # Azure config
├── .env.example                 # Environment template
├── DEPLOYMENT_GUIDE.md          # Detailed deployment steps
└── README.md
```

## 🔌 API Endpoints

### Elections
```
GET    /api/elections              # List all elections
GET    /api/elections/{id}         # Get election details
POST   /api/elections              # Create election (admin)
PUT    /api/elections/{id}         # Update election (admin)
POST   /api/elections/{id}/activate # Activate election (admin)
POST   /api/elections/{id}/close   # Close election (admin)
```

### Candidates
```
GET    /api/elections/{id}/candidates           # List candidates
POST   /api/elections/{id}/candidates           # Add candidate (admin)
GET    /api/elections/{id}/candidates?position=President
```

### Voting
```
POST   /api/elections/{id}/vote                 # Cast vote
GET    /api/elections/{id}/results              # Get results
GET    /api/elections/{id}/results/{position}   # Position results
```

## 🔐 Authentication

The system supports two role types:

### Voter
- View elections and candidates
- Cast one vote per election
- View live results

### Admin
- Create and manage elections
- Add candidates
- Activate/close elections
- View voting statistics

### Login
```javascript
// Use the Login component or API directly
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

## 📊 Database Schema

### Elections Collection
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  status: "draft" | "active" | "closed" | "completed",
  total_seats: Number,
  start_date: Date,
  end_date: Date,
  created_at: Date,
  updated_at: Date
}
```

### Candidates Collection
```javascript
{
  _id: ObjectId,
  election_id: String,
  name: String,
  position: String,
  bio: String,
  image_url: String,
  batch_year: Number,
  department: String,
  contact_email: String,
  platform: String,
  created_at: Date
}
```

### Votes Collection
```javascript
{
  _id: ObjectId,
  election_id: String,
  candidate_id: String,
  voter_id: String,
  voter_email: String,
  created_at: Date
}
```

## ⚙️ Configuration

### Customize Number of Seats
Edit the `create_election` call in `AdminDashboard.jsx`:
```javascript
total_seats: 10  // Change this value
```

### Adjust Auto-Refresh Rate
In `LiveResults.jsx`:
```javascript
const interval = setInterval(fetchResults, 5000); // Change from 5000ms
```

## 🧪 Testing

### Test Voting Flow
1. Navigate to Elections page
2. Click "Vote Now" on an active election
3. Select a candidate and click "Vote"
4. Check Live Results to see your vote recorded

### Test Admin Features
1. Login as admin
2. Go to Admin Dashboard
3. Create test election
4. Add test candidates
5. Activate election
6. Test voting flow

## 📱 Responsive Design

The platform is fully responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Tablets (iPad, Android)
- Mobile phones (iOS, Android)

## 🔧 Advanced Configuration

### Environment Variables
```bash
MONGODB_CONNECTION_STRING=  # MongoDB Atlas connection
JWT_SECRET=                 # Secret key for JWT tokens
REACT_APP_API_URL=         # API base URL
ADMIN_EMAIL=               # Admin email for setup
```

### MongoDB Collections
Automatically created on first run:
- `elections` - Election documents
- `candidates` - Candidate profiles
- `votes` - Vote records
- `voting_records` - Voter participation tracking

## 🚨 Security Notes

- All passwords are hashed with bcrypt
- JWT tokens expire after 24 hours
- CORS is configured for your domain
- MongoDB encryption at rest
- HTTPS/TLS for all communications

## 📈 Scaling Considerations

### For 1,000+ voters:
1. Use MongoDB paid tier for better performance
2. Enable read replicas for candidate data
3. Implement caching for results
4. Monitor Function App execution time

### For 10,000+ voters:
1. Use Azure Cosmos DB instead of MongoDB
2. Implement result aggregation pipeline
3. Add Redis cache for results
4. Use Azure CDN for static content

## 🐛 Troubleshooting

### API Not Responding
1. Check Azure Function is running: `az functionapp show --name <app-name>`
2. Verify MongoDB connection string
3. Check Function App logs in Azure Portal

### Vote Not Recording
1. Ensure voter hasn't already voted
2. Check MongoDB connection
3. Verify authentication token is valid

### Results Not Updating
1. Check auto-refresh is enabled
2. Verify API endpoint is correct
3. Check browser console for errors

## 📚 Documentation

- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions
- **[API Documentation](./api/README.md)** - Detailed API reference
- **[Frontend Guide](./frontend/README.md)** - Frontend components guide

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -am 'Add my feature'`
3. Push to branch: `git push origin feature/my-feature`
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Support

For issues and questions:
1. Check documentation
2. Review existing issues on GitHub
3. Create new issue with detailed description

## 🎉 Getting Started Checklist

- [ ] Clone repository
- [ ] Set up MongoDB Atlas
- [ ] Configure .env file
- [ ] Install dependencies
- [ ] Run locally (backend + frontend)
- [ ] Test voting workflow
- [ ] Deploy to Azure
- [ ] Configure CI/CD
- [ ] Set up monitoring
- [ ] Launch election!

---

**Built with**: React, Python, MongoDB, Azure Functions, Azure Static Web Apps

**Version**: 1.0.0  
**Last Updated**: 2024
