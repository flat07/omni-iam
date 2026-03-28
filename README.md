# 🚀 Omni-IAM (Omni Identity & Access Management)

A **production-ready FastAPI template** for building scalable, multi-tenant Identity & Access Management systems.

Designed for **solo developers** who want a clean, extensible foundation with modern tooling and best practices.

---

## 📌 Project Vision

Omni-IAM is a **multi-tenant IAM system** that supports:

* 🔐 Authentication & Authorization (RBAC)
* 🏢 Multi-vendor (tenant-based architecture)
* 📍 Multi-location support
* 🌐 Subdomain-based tenant routing
* ⚡ FastAPI-first, async-ready backend

---

## 🧱 Tech Stack

* **Backend**: FastAPI
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Migrations**: Alembic
* **Validation**: Pydantic v2
* **Auth**: JWT (python-jose), Passlib (bcrypt)
* **Package Manager**: `uv`

---

## ⚙️ Installation

### 1. Install dependencies

```bash
uv add fastapi uvicorn[standard]
uv add sqlalchemy alembic asyncpg psycopg2-binary
uv add "python-jose[cryptography]" "passlib[bcrypt]" python-multipart
uv add pydantic[email] pydantic-settings
```

---

### 2. Run the app

```bash
uvicorn main:app --reload
```

---

## 🏗️ Architecture Overview

### 🔑 Core Concepts

| Concept        | Description                               |
| -------------- | ----------------------------------------- |
| **Vendor**     | Tenant (company using the system)         |
| **Location**   | Physical or logical branch                |
| **Department** | Functional unit (IT, Housekeeping, etc.)  |
| **User**       | System user                               |
| **Group**      | Role (Admin, Manager, Staff)              |
| **Permission** | Action (tickets:read, users:create, etc.) |

---

## 🧠 Multi-Tenancy Strategy

* ✅ **Single database**
* ✅ Tenant isolation via `vendor_id`
* ✅ Subdomain-based routing:

```
vendor1.omni-iam.com → vendor_id = 1
vendor2.omni-iam.com → vendor_id = 2
```

Handled in:

```
app/core/deps.py
```

---

## 🔐 RBAC Model

```
User → Group → Permission
```

* Users belong to groups
* Groups have permissions
* Permissions are string-based (e.g. `tickets:create`)

---

## 📁 Project Structure

```
.
├── app
│   ├── api/v1          # API endpoints
│   ├── core            # Config, security, dependencies
│   ├── crud            # Database logic
│   ├── db              # Session, base, seeds
│   │   └── seed        # Initial data population
│   ├── models          # SQLAlchemy models
│   └── schemas         # Pydantic schemas
├── main.py             # App entry point
└── pyproject.toml      # Dependencies
```

---

## 🌱 Seeding System

Located in:

```
app/db/seed/
```

Includes:

* Vendors
* Locations
* Departments
* Users
* Groups & Permissions

### Run seed:

```bash
python -m app.db.seed.run
```

---

## 🔑 Authentication Flow

1. User logs in
2. JWT token is issued
3. Token includes:

   * `sub` (user_id)
   * `vendor_id`
4. Protected routes use dependency injection

---

## 🧩 API Modules

| Module     | Description                  |
| ---------- | ---------------------------- |
| `auth.py`  | Login, token                 |
| `users.py` | User management              |
| `org.py`   | Vendor, location, department |

---

## 🧪 Example Permissions

```
tickets:read
tickets:create
tickets:update
tickets:delete
users:read
users:create
users:update
users:delete
```

---

## 🚀 Development Roadmap

### ✅ Completed

* [x] Project structure
* [x] Models
* [x] RBAC system
* [x] Seeding
* [x] Auth (JWT login)

### 🔜 Next Steps

* [ ] Permission-based route protection (FastAPI dependencies)
* [ ] Subdomain tenant resolver middleware
* [ ] Audit logs
* [ ] Refresh tokens
* [ ] User invite system
* [ ] Admin UI (React)

---

## 🧑‍💻 Philosophy

* Keep it **simple but scalable**
* Build **real SaaS-ready architecture**
* Avoid over-engineering early
* Focus on **clean domain modeling**

---

## ⚠️ Notes

* This is a **template**, not a finished product
* Optimized for **learning + production evolution**
* Built by a **solo developer mindset**

---

## 🤝 Contribution

Currently a solo project, but structured for future collaboration.

---

## 📄 License

MIT License

---

## 💡 Final Thought

This project is designed to grow into a **full IAM backbone** for:

* SaaS apps
* Hotel systems
* Internal tools
* Multi-tenant platforms

Build once. Reuse everywhere.
