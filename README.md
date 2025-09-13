
# Vehicle Parking App

Vehicle Parking App is a comprehensive full-stack solution for managing vehicle parking lots, designed for both administrators and end-users. The system provides a seamless experience for parking lot management, spot reservation, user authentication, and real-time notifications. Built with a modern Vue.js frontend and a robust Flask backend, it leverages JWT for secure authentication and Celery/Redis for background processing and scheduled tasks. The app is designed to be highly responsive, accessible, and easy to deploy on Windows, Mac, or Linux.

Key highlights:
- Intuitive dashboards for both admins and users
- Secure login and registration flows
- Real-time updates and notifications
- Automated email reminders and CSV exports
- Docker-based Redis setup for easy cross-platform compatibility

---


## Features

- **User Authentication & Authorization:**
   - Secure registration and login for users and admins using JWT tokens
   - Role-based access control for admin and user features

- **Admin Dashboard:**
   - Add, edit, and delete parking lots
   - View all registered users and their details
   - Search users by name
   - View summary statistics (revenue, occupancy, lot shares)
   - Manage parking spots (delete, view status)

- **User Dashboard:**
   - Search for available parking lots by location or pincode
   - Reserve and release parking spots
   - View recent parking history and reservation details
   - Export parking history as CSV via email
   - View summary of active and past reservations, total amount spent

- **Parking Spot Management:**
   - Real-time status for available, occupied, and warning spots
   - Color-coded spot indicators for accessibility

- **Notifications & Background Tasks:**
   - Automated email for monthly parking history report, daily reminders for parking, and user-triggered parking report (.csv) to user's email
   - Scheduled tasks using Celery and Redis

---

## Folder Structure
```
Vehicle_Parking_App/
├── backend/           # Flask backend (API, models, routes)
├── frontend/          # Vue.js frontend (SPA)
├── tasks/             # Celery tasks
├── instance/          # SQLite DB
├── celery_app.py      # Celery app config
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

---

## Prerequisites
- Python 3.10+
- Node.js & npm
- Docker (for Redis)

---

## Backend Setup
1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run Flask backend:**
   ```bash
   python -m backend.app
   ```

---

## Frontend Setup
1. **Install Node dependencies:**
   ```bash
   cd frontend
   npm install
   ```
2. **Run Vue development server:**
   ```bash
   cd frontend
   npm run serve
   ```

---


## Redis Setup

You can run Redis either using Docker (recommended for Windows) or via WSL (Windows Subsystem for Linux).

### Option 1: Redis via Docker
If you do NOT have WSL or a native Redis installation, use Docker:

1. **Pull Redis image:**
   ```bash
   docker pull redis
   ```
2. **Run Redis container:**
   ```bash
   docker run -d --name redis-server -p 6379:6379 redis
   ```

### Option 2: Redis via WSL (Windows Subsystem for Linux)
If you have WSL installed, you can run Redis natively:

1. **Open your WSL terminal (Ubuntu or other distribution).**
2. **Update package lists:**
   ```bash
   sudo apt update
   ```
3. **Install Redis:**
   ```bash
   sudo apt install redis-server
   ```
4. **Start Redis server:**
   ```bash
   sudo service redis-server start
   ```
5. **Check Redis status:**
   ```bash
   sudo service redis-server status
   ```
6. Redis will be available at `localhost:6379` for your backend and Celery workers.

---

## Celery Setup
Celery is used for background tasks (CSV export, reminders).

1. **Start Celery worker:**
   ```bash
   celery -A celery_app.celery_app worker --pool=solo --loglevel=INFO
   ```
2. **Start Celery beat (scheduler):**
   ```bash
   celery -A celery_app.celery_app beat --loglevel=INFO
   ```

---

## Environment Variables
- Set your Flask secret keys, JWT secret, and mail credentials in environment variables or `.env` file.
- Example:
  ```env
  APP_SECRET_KEY=your-secret-key
  JWT_SECRET_KEY=your-jwt-secret-key
  MAIL_USERNAME=your-email@gmail.com
  MAIL_PASSWORD=your-email-password
  MAIL_DEFAULT_SENDER=your-email@gmail.com
  ```

---

## Usage
- Access the frontend at `http://localhost:8080` (default Vue port)
- Backend API runs at `http://127.0.0.1:5000`
- Admin and user dashboards available after login

---

## Troubleshooting
- If you see Redis connection errors, ensure Docker Redis is running (`docker ps`)
- For Windows users, Docker Desktop is recommended for Redis
- If you change ports, update configs in both backend and frontend

---

## License
MIT

---

## Credits
- Vue.js
- Flask
- Celery
- Redis
- Bootstrap