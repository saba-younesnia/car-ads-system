
# 🚗 Car Advertisement & Transaction Management System

A production-oriented **full-stack car marketplace application** built with **Flask, PostgreSQL, SQLAlchemy, Alembic, Docker, and JavaScript**.

The project goes beyond a simple CRUD application by implementing **role-based access control, advertisement management, advanced car search, transaction workflows, ownership-related data modeling, database migrations, containerized deployment, and a responsive browser-based interface**.

It is designed as a modular foundation for a scalable automotive marketplace where users can publish vehicles, search listings, initiate transactions, and manage marketplace operations according to their roles.

---

## ✨ Key Features

### 🔐 Authentication & Authorization

* User registration and login
* Password hashing using Werkzeug
* Session-based authentication on the Flask backend
* Active/inactive user management
* Role-based access control (RBAC)
* Protected routes using reusable decorators
* Permission checks at the backend level
* Role-aware frontend UI

Supported roles include:

* `Admin`
* `Senior`
* `Moderator`
* `System`
* `Seller`
* `User`

The authorization layer is implemented through reusable decorators such as:

* `login_required`
* `roles_required`

This keeps authentication and authorization logic centralized instead of duplicating it across individual endpoints.

---

### 👤 User Management

Administrators and senior users can access a dedicated user-management interface.

Capabilities include:

* View registered users
* Inspect assigned roles
* Check account status
* Deactivate users
* Prevent users from accessing the system after deactivation

The backend validates authorization independently from the frontend, ensuring that hiding a UI button does not become the security boundary.

---

### 🚘 Advertisement Management

Authenticated users can create vehicle advertisements containing:

* Make
* Model
* Year
* Color
* Vehicle status
* Advertisement title
* Description
* Price

The application also supports:

* Advertisement listing
* Advertisement deletion
* Publisher information
* Creation timestamps
* Role-aware advertisement actions
* Seller-specific permissions

The data model separates **vehicle information** from **advertisement information**, allowing the same vehicle domain model to participate in additional workflows such as transactions, price history, images, and ownership history.

---

### 🔎 Advanced Car Search

The frontend provides an advanced search interface supporting:

* Minimum price
* Maximum price
* Brand / make
* Color
* Vehicle status

Search parameters are converted into URL query parameters and sent to the backend through a dedicated search API.

This provides a cleaner separation between:

```text
Search UI
    ↓
HTTP API
    ↓
Database query
    ↓
Filtered vehicle results
```

---

### 🔗 Related Vehicle Discovery

Users can inspect vehicles related to a selected car.

The application exposes a dedicated related-car workflow:

```text
Advertisement
      ↓
Vehicle
      ↓
Related Vehicles
```

This provides a foundation for implementing more sophisticated recommendation or similarity mechanisms in the future.

---

### 💳 Transaction Workflow

The project models a marketplace transaction lifecycle between buyers and sellers.

A transaction contains:

* Buyer
* Seller
* Vehicle
* Agreed price
* Transaction date
* Status

The frontend supports workflow actions such as:

```text
Pending
   ↓
Accepted / Rejected
   ↓
Completed
```

Depending on the user's role and relationship to the transaction, the UI exposes appropriate actions such as:

* Initiate transaction
* Accept transaction
* Reject transaction
* Mark transaction as completed

The backend remains responsible for enforcing the actual authorization rules.

---

### 🗂️ Transaction Management

Authorized users can access transaction information including:

* Transaction ID
* Vehicle
* Buyer
* Seller
* Agreed price
* Status
* Transaction date

Administrators and senior users can manage transactions globally, while ordinary marketplace users can work with transactions relevant to their role.

---

## 🏗️ Architecture

The application follows a layered architecture separating:

```text
Frontend
   │
   ▼
REST / HTTP API
   │
   ▼
Authentication & Authorization
   │
   ▼
Application / Domain Logic
   │
   ▼
SQLAlchemy ORM
   │
   ▼
PostgreSQL
```

The frontend is intentionally kept separate from backend business logic.

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* Fetch API
* Font Awesome

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Werkzeug
* Flask-Migrate
* PostgreSQL

### Infrastructure

* Docker
* Docker Compose
* PostgreSQL container
* pgAdmin

---

# 🗄️ Database Design

The database is implemented using **PostgreSQL** and SQLAlchemy.

The initial Alembic migration defines the following core entities:

users
  │
  ├──────── user_roles ─────── roles
  │
  ├──────── advertisements ─── cars
  │                              │
  │                              ├── car_images
  │                              ├── ownership_history
  │                              └── price_history
  │
  └──────── transactions ────────┘
```

### Core Tables

#### `users`

Stores marketplace users and authentication information.

Key fields:

* `id`
* `mobile_number`
* `password_hash`
* `active`

---

#### `roles`

Stores application roles independently from users.

roles
-----
id
name
```

The unique role constraint prevents duplicate role definitions.

---

#### `user_roles`

Implements the many-to-many relationship between users and roles.

This allows a single user to have multiple permissions without hard-coding a single role into the user record.

---

#### `cars`

Stores vehicle-specific information:

* Make
* Model
* Year
* Color
* Status

Indexes are defined for frequently queried fields such as:

* `make`
* `color`
* `status`

---

#### `advertisements`

Represents marketplace listings independently from the underlying vehicle.

Important relationships include:

advertisement → car
advertisement → publisher
```

The schema also includes:

* Price indexing
* Unique vehicle-to-advertisement relationship
* Cascade behavior for associated vehicles
* Nullable publisher relationship

---

#### `car_images`

Provides a dedicated structure for storing vehicle image metadata.

This creates a natural extension point for:

* Image uploads
* Image search
* Computer vision
* Image embeddings
* Multimodal retrieval

---

#### `ownership_history`

Tracks historical ownership of vehicles.

This enables the system to evolve beyond a simple marketplace into a more complete vehicle lifecycle platform.

---

#### `price_history`

Stores historical price changes for vehicles.

This creates a foundation for future functionality such as:

* Price trend visualization
* Price analytics
* Market intelligence
* Price prediction

---

#### `transactions`

Represents the actual buyer/seller transaction.

Foreign-key constraints protect referential integrity between:

Buyer
Seller
Car
Transaction
```

The schema uses restrictive deletion behavior where transaction history should not be silently invalidated.

---

# 🔐 Authorization Architecture

One of the important design decisions is that authorization is implemented on the backend rather than relying exclusively on frontend visibility.

For example:

```python
@roles_required('Admin', 'Senior')
def protected_endpoint():
    ...
```

The reusable authorization decorator performs:

1. Authentication check
2. User lookup
3. Active-account validation
4. Current-user assignment
5. Role validation
6. Permission rejection with HTTP `403`

Conceptually:

```text
HTTP Request
     │
     ▼
Is user authenticated?
     │
   No ──────► Login
     │
    Yes
     ▼
Does user exist?
     │
   No ──────► Session cleared
     │
    Yes
     ▼
Is account active?
     │
   No ──────► Access denied
     │
    Yes
     ▼
Does user have required role?
     │
   No ──────► HTTP 403
     │
    Yes
     ▼
Protected endpoint
```

This provides a reusable security boundary for future API endpoints.

---

# 🧩 Database Migrations

The project uses **Flask-Migrate / Alembic** instead of relying solely on `db.create_all()`.

The migration history captures schema changes in version-controlled files.

Example:

```text
migrations/
└── versions/
    └── 17991e890eec_initial_database_schema.py
```

The migration defines:

* Tables
* Primary keys
* Foreign keys
* Unique constraints
* Indexes
* Cascade rules
* Referential integrity

This makes database schema evolution reproducible across development and deployment environments.

---

# 🐳 Dockerized Development Environment

The project includes a complete Docker Compose environment.

```text
                  Docker Compose
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
       Flask        PostgreSQL     pgAdmin
       :5000          :5432         :8080
```

### Web Container

The Flask application runs on:

0.0.0.0:5000
```

### PostgreSQL

The database is isolated in its own container and persisted using a Docker volume:

pgdata
```

### pgAdmin

pgAdmin provides a graphical interface for inspecting and managing the PostgreSQL database during development.

---

# ⚙️ Environment Configuration

The application supports environment-based configuration.

Important variables include:

```
SQLALCHEMY_DATABASE_URI
SECRET_KEY
```

Docker Compose injects the PostgreSQL connection string using the service name:

```
db
```

This allows the Flask container to communicate with PostgreSQL without hard-coding a localhost database connection.

---

# 🚀 Running the Project

## Option 1 — Docker Compose

Clone the repository:

```bash
git clone <repository-url>
cd car-advertisement-system
```

Start the complete environment:

```bash
docker compose up --build
```

The services become available at:

```
Flask application:
http://localhost:5000

pgAdmin:
http://localhost:8080

PostgreSQL:
localhost:5432
```

Stop the environment:

```bash
docker compose down
```

To remove the persistent database volume as well:

```bash
docker compose down -v
```

> Do not use the `-v` option when you want to preserve the development database.

---

# 🌱 Database Initialization

The project includes a database seeding script:

```bash
python seed_db.py
```

The seed process:

1. Creates database tables if necessary.
2. Creates the predefined roles.
3. Creates the initial administrator account.
4. Assigns the `Admin` role to that account.

The predefined roles are:

```
Admin
User
Moderator
System
Senior
Seller
```

For production deployments, default credentials should be replaced with secure credentials supplied through environment variables or a secret-management system.

---

# 🧪 API-Oriented Design

The frontend communicates with the Flask backend through HTTP endpoints.

Representative API operations include:

```
POST   /api/register
POST   /login_api
POST   /logout

GET    /api/advertisements
POST   /api/advertisements
DELETE /api/advertisements/<id>

GET    /api/search/cars
GET    /api/cars/<id>/related

GET    /api/users
PUT    /api/users/<id>/deactivate

GET    /api/transactions
POST   /api/transactions
PUT    /api/transactions/<id>/status
```

This API-oriented structure makes the backend suitable for future clients such as:

* React
* Vue
* Mobile applications
* External marketplace services
* Automated integrations

---

# 🎨 Frontend

The frontend is implemented using lightweight browser technologies rather than a large JavaScript framework.

The main interface contains dedicated sections for:

```
Authentication
     │
     ├── Register
     └── Login
     
Marketplace
     │
     ├── Advertisements
     ├── Create Advertisement
     ├── Advanced Search
     └── Related Cars
     
Administration
     │
     ├── User Management
     └── Transaction Management
```

The JavaScript layer dynamically updates the UI according to:

* Authentication state
* Current user
* Assigned roles
* Advertisement ownership
* Transaction status

---

# 🔄 Marketplace Workflow

A typical marketplace flow looks like:

```
User Registration
       │
       ▼
     Login
       │
       ▼
Browse Advertisements
       │
       ├───────────────┐
       │               │
       ▼               ▼
Advanced Search    View Related Cars
       │
       ▼
Select Vehicle
       │
       ▼
Initiate Transaction
       │
       ▼
     Pending
       │
   ┌───┴────┐
   ▼        ▼
Accepted  Rejected
   │
   ▼
Completed
```

This workflow demonstrates that the application is not simply a CRUD interface; it models a basic business process.

---

# 🌿 Git & Branching Strategy

The project is developed using feature-oriented Git branches.

The repository separates major areas of development into branches rather than implementing every feature directly on a single branch.

For example, the development history includes dedicated work around:

```
main
 │
 ├── feature/multimodal_embeddings
 │
 ├── indexing
 │
 └── vectorization
```

The purpose of this strategy is to keep major architectural changes isolated and easier to review.

### Recommended workflow

```
main
 │
 └── feature branch
        │
        ├── focused commits
        │
        ├── tests
        │
        └── review
             │
             ▼
          merge
```

Commits should represent logical units of work rather than large collections of unrelated changes.

For example:

```
feat: implement role-based authorization
feat: add advertisement management
feat: implement advanced car search
feat: add transaction workflow
feat: add database migrations
feat: containerize application
```

This makes the Git history easier for another engineer or recruiter to understand.

---

# 📌 Engineering Strengths

The project demonstrates several engineering practices that are valuable in professional backend and AI-oriented development environments.

### 1. Role-Based Access Control

Authorization is modeled explicitly through roles and reusable decorators instead of scattered permission checks.

### 2. Relational Data Modeling

The application uses normalized domain entities and explicit relationships rather than storing everything inside a single table.

### 3. Referential Integrity

Foreign keys and deletion strategies protect the consistency of relationships between users, cars, advertisements, and transactions.

### 4. Database Indexing

Frequently searched fields such as vehicle make, color, status, and advertisement price have database indexes.

### 5. Migration-Based Schema Management

Alembic migrations make schema changes reproducible and version controlled.

### 6. Containerization

Docker Compose provides a reproducible multi-service development environment.

### 7. Separation of Concerns

The application separates:

```
UI
API
Authentication
Authorization
ORM
Database
Infrastructure
```

### 8. Extensibility

The schema already contains natural extension points for:

* Vehicle images
* Ownership history
* Price history
* Recommendation systems
* Image embeddings
* Semantic search
* Multimodal retrieval

---

# 🔮 Future Improvements

The current architecture provides a strong foundation for additional production-grade functionality.

Potential next steps include:

### Security

* Replace the current frontend placeholder authentication token with real JWT or secure session-based authentication.
* Move all secrets and default credentials to environment variables.
* Add CSRF protection where appropriate.
* Add rate limiting.
* Implement secure password policies.
* Add refresh-token/session management where required.

### Backend

* Split the Flask application into blueprints.
* Introduce service and repository layers.
* Add request validation schemas.
* Add centralized error handling.
* Add API documentation using OpenAPI/Swagger.
* Add structured application logging.

### Testing

Introduce automated:

```
Unit Tests
    +
Integration Tests
    +
API Tests
    +
Database Tests
```

with CI execution through GitHub Actions.

### Marketplace

Future marketplace functionality could include:

* Image uploads
* Favorites
* Seller profiles
* Messaging
* Offers and negotiation
* Pagination
* Sorting
* Advanced filtering
* Notifications
* Payment integration

### AI / Multimodal Search

The existing `car_images` and related architecture provide a natural path toward AI-powered search:

```
Car Image
    │
    ▼
Image Encoder
    │
    ▼
Image Embedding
    │
    ▼
Vector Store
    │
    ▼
Similarity Search
    │
    ▼
Related Vehicles
```

This can evolve into a multimodal retrieval system combining:

```
Text ─────────┐
              ├──► Embedding Space ───► Vector Search
Images ───────┘
```

Such an architecture can support use cases such as:

> "Find cars visually similar to this image."

or:

> "Find a black BMW under a specific price range."

---

# 🛠️ Technology Stack

| Layer                         | Technology                    |
| ----------------------------- | ----------------------------- |
| Language                      | Python                        |
| Backend                       | Flask                         |
| ORM                           | Flask-SQLAlchemy / SQLAlchemy |
| Database                      | PostgreSQL                    |
| Migrations                    | Flask-Migrate / Alembic       |
| Authentication                | Flask session + Werkzeug      |
| Password Security             | Werkzeug Password Hashing     |
| Frontend                      | HTML / CSS / JavaScript       |
| HTTP Client                   | Fetch API                     |
| Containerization              | Docker                        |
| Orchestration                 | Docker Compose                |
| Database UI                   | pgAdmin                       |
| Cross-Origin Support          | Flask-CORS                    |
| Forms / Validation Foundation | Flask-WTF                     |
| Version Control               | Git                           |
