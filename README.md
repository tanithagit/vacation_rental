#  StayFinder - Vacation Rental Platform

A full-stack vacation rental booking platform similar to Airbnb, built with FastAPI and React.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)

---

##  Features

###  Host Features
- Register and login as a host
- Create and manage property listings
- Upload property images
- Set pricing and availability
- View booking dashboard with revenue analytics
- Receive email notifications for new bookings

###  Guest Features
- Register and login as a guest
- Search properties by location
- Filter by price range, guest count, and dates
- Book properties with conflict prevention
- Make payments via Stripe
- Leave reviews after completed stays
- View booking history

###  Admin Features
- Monitor users and properties
- Moderate reviews and listings

---

##  Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| FastAPI | REST API framework |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| JWT | Authentication |
| Stripe | Payment processing |
| Mailtrap/SMTP | Email notifications |
| Pytest | Testing |

### Frontend
| Technology | Purpose |
|-----------|---------|
| React 18 | UI framework |
| Vite | Build tool |
| Tailwind CSS | Styling |
| React Router | Navigation |
| Axios | API calls |

---

##  Project Structure

---

##  Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Stripe account (for payments)
- Mailtrap account (for email testing)

### 1. Clone the Repository
```bash
git clone https://github.com/tanithagit/vacation_rental.git
cd vacation_rental
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/vacation_rental
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
```

### 4. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE vacation_rental;
\q

# Run migrations
alembic upgrade head
```

### 5. Run Backend

```bash
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**
API Docs at: **http://localhost:8000/docs**

### 6. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

##  Booking Flow

---

##  Payment Integration

We use **Stripe** for secure payment processing:

### Test Card Numbers (Stripe Test Mode)

---

##  Critical Booking Rules

| Rule | Implementation |
|------|---------------|
| No double booking | Check overlapping dates before confirming |
| Future dates only | Validate check-in > today |
| Valid date range | Check-out must be after check-in |
| No self-booking | Host cannot book own property |
| One review per booking | Check existing review before creating |
| Completed stays only | Booking must be completed to review |

---

## 📧 Email Notifications

Emails are sent automatically for:
-  Booking confirmation (to guest)
-  Payment confirmation (to guest)
-  New booking notification (to host)
-  Booking cancellation (to guest)

---

##  Authentication

- JWT-based authentication
- Passwords hashed with bcrypt
- Role-based access control (host/guest/admin)
- Token expires after 30 minutes

---

##  Running Tests

```bash
cd backend

# Create test database
psql -U postgres -c "CREATE DATABASE vacation_rental_test;"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_bookings.py -v
```

### Test Coverage

---

##  API Endpoints

### Authentication

### Payments

### Reviews

---

##  Bonus Features Implemented

-  Role-based access control (host/guest/admin)
-  Property search with multiple filters
-  Pagination for search results
-  Average rating calculation
-  Host revenue dashboard
-  Email notifications via Mailtrap
-  Comprehensive test suite (36 tests)

---

##  Developer

**Anitha T**
GitHub: [@tanithagit](https://github.com/tanithagit)