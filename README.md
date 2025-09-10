# Shipments Manager

A full-stack application for managing shipments with a modern React frontend and FastAPI backend.

## Features

- **CRUD Operations**: Create, read, update, and delete shipments
- **Real-time Updates**: Optimistic updates with React Query
- **Filtering & Search**: Filter by status and search by title/destination
- **Sorting**: Sort by creation date, ETA, or title
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **Docker Support**: Containerized for easy deployment
- **CI/CD**: Automated deployment to AWS ECS

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **Pandas** - Excel data processing
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **TanStack Query** - Data fetching and caching
- **React Hook Form** - Form handling

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local development
- **AWS ECR** - Container registry
- **AWS ECS** - Container orchestration
- **GitHub Actions** - CI/CD pipeline

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Local Development with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shipments-manager
   ```

2. **Start the application**
   ```bash
   docker compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development (without Docker)

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/shipments` | Get all shipments |
| POST | `/shipments` | Create a new shipment |
| PATCH | `/shipments/{id}` | Update a shipment |
| DELETE | `/shipments/{id}` | Delete a shipment |
| GET | `/health` | Health check |

## Environment Variables

### Backend
- `ALLOWED_ORIGINS` - CORS allowed origins (default: `*`)
- `PORT` - Server port (default: `8000`)

### Frontend
- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)

## Data Model

### Shipment
```typescript
interface Shipment {
  id: string;           // UUID
  title: string;        // Required
  destination?: string; // Optional
  eta?: string;         // ISO date string
  status: 'pending' | 'completed';
  created_at: string;   // ISO datetime
  updated_at: string;   // ISO datetime
}
```

## AWS Deployment

### Prerequisites
1. AWS CLI configured
2. ECR repositories created
3. ECS cluster and service configured
4. GitHub repository secrets set

### Required GitHub Secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (optional, defaults to us-east-1)

### ECR Repositories
Create the following repositories in AWS ECR:
```bash
aws ecr create-repository --repository-name shipments-backend
aws ecr create-repository --repository-name shipments-frontend
```

### ECS Task Definition
Your ECS task definition should include:
- **Backend container**: Port 8000, health check on `/health`
- **Frontend container**: Port 80, health check on `/health`

### Environment Variables in Workflow
Update the following in `.github/workflows/deploy.yml`:
```yaml
env:
  AWS_REGION: us-east-1
  ECR_BACKEND_REPO: shipments-backend
  ECR_FRONTEND_REPO: shipments-frontend
  ECS_CLUSTER: your-ecs-cluster-name
  ECS_SERVICE: your-ecs-service-name
  TASK_DEF_FAMILY: your-taskdef-family
  CONTAINER_BACKEND: backend
  CONTAINER_FRONTEND: frontend
```

## Database Migration (Future)

The current implementation uses in-memory storage. To switch to SQLite:

1. **Install SQLModel**
   ```bash
   pip install sqlmodel
   ```

2. **Update backend/app/main.py**
   ```python
   from sqlmodel import SQLModel, create_engine, Session
   
   engine = create_engine("sqlite:///shipments.db")
   SQLModel.metadata.create_all(engine)
   
   def get_session():
       with Session(engine) as session:
           yield session
   ```

3. **Replace in-memory storage with database operations**

## Development

### Project Structure
```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # Pydantic models
│   │   ├── deps.py          # Dependencies
│   │   └── __init__.py
│   ├── data/
│   │   └── seed_shipments.xlsx
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── types.ts        # TypeScript types
│   │   ├── api.ts          # API client
│   │   └── App.tsx         # Main app component
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .github/workflows/deploy.yml
└── README.md
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Linting
```bash
# Backend
cd backend
black .
flake8 .

# Frontend
cd frontend
npm run lint
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
