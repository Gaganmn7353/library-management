# Library Management System

A complete library management system with Flask backend and modern web interface.

## Features
- Add/Remove Books
- Add/Remove Users
- Issue/Return Books
- Export data to CSV
- Search functionality
- SQLite database

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open browser and go to: `http://localhost:5000`

## Database
- SQLite database (library.db) is automatically created
- No manual setup required

## API Endpoints
- GET /api/books
- POST /api/books
- DELETE /api/books/<id>
- GET /api/users
- POST /api/users
- DELETE /api/users/<id>
- GET /api/transactions
- POST /api/transactions/issue
- PUT /api/transactions/return/<id>
- GET /api/export/books
- GET /api/export/users
- GET /api/export/transactions
```

## 📁 Complete File Structure:
```
library-system/
├── app.py                    # Main Flask application (COPY FROM ARTIFACT)
├── templates/
│   └── index.html           # Frontend HTML (COPY FROM ABOVE)
├── requirements.txt         # Python dependencies (COPY FROM ABOVE)
├── README.md               # Documentation (COPY FROM ABOVE)
└── library.db              # SQLite database (auto-generated)