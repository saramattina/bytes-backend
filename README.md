![alt text](./images/image%20copy.png)

# 🍔 Bytes.AI Backend

The backend for **Bytes.AI**, an intelligent recipe management application that blends creative AI with smart grocery list management.
Built with **Django**, powered by **OpenAI GPT-4o-mini**, secured with **JWT authentication**, and deployed on **Railway**.

---

## 🍜 Overview

The Bytes.AI backend provides the core API and business logic for the app.
It handles:

- **AI-powered recipe generation** using OpenAI's GPT-4o-mini with dietary tag enforcement and unit normalization
- **Secure image storage** via AWS S3 with presigned URLs and automatic cleanup
- **Intelligent grocery list management** with unit conversion, item merging, and recipe-to-list import
- **Comprehensive user authentication** including JWT tokens, password reset via SendGrid email, and profile management
- **Full recipe CRUD operations** with nested ingredients and steps
- **RESTful API design** with 22 functional endpoints serving the React frontend

This service powers all frontend interactions, exposing RESTful endpoints and managing authentication, data persistence, and external integrations.

---

## 🧑‍💻 Technologies Used

| Technology                       | Purpose                                       |
| -------------------------------- | --------------------------------------------- |
| **Django 4.2.25**                | Core backend framework                        |
| **Django REST Framework 3.16.1** | REST API serialization and routing            |
| **Simple JWT 5.5.1**             | JSON Web Token authentication                 |
| **OpenAI API (GPT-4o-mini)**     | AI recipe generation with dietary constraints |
| **AWS S3 (boto3)**               | Cloud image storage with presigned URLs       |
| **SendGrid**                     | Email delivery for password resets            |
| **PostgreSQL**                   | Production database (Railway)                 |
| **WhiteNoise**                   | Static file serving                           |
| **Gunicorn**                     | Production WSGI server                        |
| **Railway**                      | Cloud deployment and hosting                  |

---

## 🎯 Core Features

### 1. AI Recipe Generation

- **OpenAI GPT-4o-mini integration** for intelligent recipe creation
- **Prompt-based generation** - Describe what you want to cook and let AI create the recipe
- **Dietary tag enforcement** - Automatically enforces restrictions (vegan, gluten-free, no nuts, etc.)
- **Grocery list incorporation** - Generate recipes using checked items from your grocery list
- **Unit normalization** - Ensures all ingredients use standardized measurements
- **Automatic allergen detection** - AI identifies and tags common allergens
- **Detailed instructions** - Includes cooking times, temperatures, and visual cues
- **Nutrition information** - AI-generated macro and nutrition details in notes

### 2. Intelligent Grocery List Management

- **Recipe-to-list import** - Add all recipe ingredients to your grocery list with one click
- **Smart item merging** - Automatically combines quantities of duplicate items with compatible units
- **Unit conversion** - Converts between compatible measurements (tsp ↔ tbsp ↔ cup, g ↔ kg ↔ oz ↔ lb)
- **Check/uncheck tracking** - Mark items as purchased or needed
- **Bulk operations** - Clear all checked items at once
- **Manual item entry** - Add individual items with custom quantities and units
- **Intelligent updates** - Adding more of an item unchecks it for re-purchase

### 3. Recipe Management

- **Full CRUD operations** - Create, read, update, and delete recipes
- **Image upload** - Store recipe photos in AWS S3 with automatic cleanup
- **Nested data** - Manage ingredients and cooking steps as structured data
- **Favorite marking** - Tag favorite recipes for quick access
- **Dietary tags** - JSON-based tag system for allergens and dietary preferences
- **User-scoped access** - Users only see their own recipes (data isolation)

### 4. User Authentication & Profile Management

- **JWT-based authentication** - Secure, stateless token authentication
- **Token refresh** - Automatic session extension without re-login
- **Password reset via email** - SendGrid-powered password recovery with 1-hour token expiry
- **Profile updates** - Change username, email, or password
- **Account deletion** - Complete data removal with cascade delete
- **Custom password validation** - Enforces uppercase, lowercase, number, and special character requirements

### 5. Image Management

- **AWS S3 storage** - Scalable, production-grade cloud storage
- **UUID-based filenames** - Prevents collisions and overwrites
- **User-specific folders** - Organized by `recipes/user_{id}/`
- **Presigned URLs** - Secure, temporary access to private images
- **Automatic deletion** - Removes old images when recipes are updated or deleted
- **MultiPart form support** - Handle image uploads with JSON data

---

## 🗄️ Database Models

### Recipe

- **Fields:** title, notes, favorite, image, tags (JSON)
- **Relationships:** One-to-Many with Ingredient and Step
- **Features:** Custom S3 upload paths, JSON dietary tags

### Ingredient

- **Fields:** name, quantity, volume_unit, weight_unit
- **Validation:** Only one unit type (volume OR weight) per ingredient
- **Supported Units:**
  - Volume: tsp, tbsp, fl_oz, cup, pt, qt, gal, ml, l
  - Weight: g, kg, oz, lb

### Step

- **Fields:** step (number), description
- **Purpose:** Ordered cooking instructions for recipes

### GroceryListItem

- **Fields:** name, quantity, volume_unit, weight_unit, checked, created_at
- **Features:** Unit conversion, duplicate merging, check/uncheck status

---

## 🔌 API Endpoints

### Authentication (6 endpoints)

| Method | Endpoint                         | Description                             |
| ------ | -------------------------------- | --------------------------------------- |
| POST   | `/users/sign-up/`                | Register new user with JWT tokens       |
| POST   | `/users/sign-in/`                | Login and receive access/refresh tokens |
| GET    | `/users/verify/`                 | Verify current JWT token                |
| POST   | `/users/token/refresh/`          | Refresh access token                    |
| POST   | `/users/password-reset/`         | Request password reset email            |
| POST   | `/users/password-reset-confirm/` | Confirm password reset with token       |

### User Profile (4 endpoints)

| Method | Endpoint                  | Description                                 |
| ------ | ------------------------- | ------------------------------------------- |
| PATCH  | `/users/update-username/` | Update username (min 3 chars, unique)       |
| PATCH  | `/users/update-email/`    | Update email with validation                |
| PATCH  | `/users/update-password/` | Change password (requires current password) |
| DELETE | `/users/delete-account/`  | Delete account with cascade                 |

### Recipes (7 endpoints)

| Method               | Endpoint                                 | Description                             |
| -------------------- | ---------------------------------------- | --------------------------------------- |
| GET/POST             | `/recipes/`                              | List user's recipes / Create new recipe |
| GET/PUT/PATCH/DELETE | `/recipes/<id>/`                         | Retrieve, update, or delete recipe      |
| GET/POST             | `/recipes/<recipe_id>/ingredients/`      | List/add ingredients                    |
| GET/PUT/PATCH/DELETE | `/recipes/<recipe_id>/ingredients/<id>/` | Ingredient CRUD                         |
| GET/POST             | `/recipes/<recipe_id>/steps/`            | List/add cooking steps                  |
| GET/PUT/PATCH/DELETE | `/recipes/<recipe_id>/steps/<id>/`       | Step CRUD                               |
| POST                 | `/recipes/generate/`                     | **AI recipe generation**                |

### Grocery List (5 endpoints)

| Method | Endpoint                                | Description                        |
| ------ | --------------------------------------- | ---------------------------------- |
| GET    | `/grocery-list/`                        | List all grocery items             |
| POST   | `/grocery-list/add-item/`               | Add single item with smart merging |
| POST   | `/grocery-list/add-recipe/<recipe_id>/` | Import recipe ingredients          |
| PATCH  | `/grocery-list/item/<item_id>/`         | Update item (check/uncheck)        |
| DELETE | `/grocery-list/clear-checked/`          | Bulk delete checked items          |

---

## 🔐 Authentication & Security

### JWT Token System

- **Access Token:** Short-lived token for API requests (sent in Authorization header)
- **Refresh Token:** Long-lived token to obtain new access tokens
- **Token Verification:** `/users/verify/` endpoint for session persistence
- **Stateless:** No server-side session storage required

### Password Security

- **Custom Validators:**
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character (`!@#$%^&*(),.?":{}|<>`)
- **Django Built-in Validators:**
  - UserAttributeSimilarityValidator
  - CommonPasswordValidator

### Data Isolation

- All queries filtered by `request.user`
- Users cannot access other users' recipes, ingredients, steps, or grocery lists
- Authorization enforced at view level with `permissions.IsAuthenticated`

### CORS & CSRF

- **Allowed Origins:**
  - `http://localhost:5173` (development)
  - `https://bytesai.netlify.app` (production)
- **CSRF Trusted Origins:**
  - Railway backend
  - Netlify frontend

---

## ⚙️ Getting Started

### 🔗 Live Links

- **Deployed Backend:** [Railway](https://bytes-backend-production.up.railway.app/)
- **Frontend App:** [Netlify](https://bytesai.netlify.app/)
- **Planning Materials (Docs, Wireframes, etc.):** [Trello](https://trello.com/b/kb8WlZb7/bytes-group-project)

---

### 🧱 Prerequisites

Ensure you have the following installed:

- **Python 3.10+**
- **pip** and **pipenv**
- **PostgreSQL** (optional - SQLite used by default in development)

You'll also need API keys for:

- **OpenAI** - For AI recipe generation
- **AWS S3** - For image storage (Access Key ID, Secret Access Key, Bucket Name)
- **SendGrid** - For password reset emails (optional in development)

---

### ⚡ Local Setup

```bash
# 1️⃣ Clone the repository
git clone https://github.com/saramattina/bytes-backend
cd bytes-backend

# 2️⃣ Activate the Pipenv shell
pipenv shell

# 3️⃣ Install dependencies
pipenv install

# 4️⃣ Create your .env file
touch .env
```

**Environment Variables (.env):**

```bash
# Django Settings
DJANGO_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# OpenAI (Required for AI recipe generation)
OPENAI_API_KEY=your-openai-api-key

# AWS S3 (Required for image uploads)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# SendGrid (Optional - email will print to console in development)
SENDGRID_API_KEY=your-sendgrid-api-key

# Frontend URL (for password reset links)
FRONTEND_URL=http://localhost:5173

# Email Settings (Development - optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@bytesai.com

# Database (Optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

```bash
# 5️⃣ Apply database migrations
python manage.py migrate

# 6️⃣ Create a superuser (optional - for Django admin)
python manage.py createsuperuser

# 7️⃣ Run the development server
python manage.py runserver
```

**Development server will run at:** `http://127.0.0.1:8000/`
**Django admin available at:** `http://127.0.0.1:8000/admin/`

---

## 🚀 Deployment

### Production Configuration

The app is deployed on **Railway** with the following production settings:

- **Database:** PostgreSQL (via DATABASE_URL)
- **Static Files:** Served by WhiteNoise
- **WSGI Server:** Gunicorn
- **Email Backend:** SendGrid API (SMTP ports blocked on Railway)

**Production Environment Variables:**

```bash
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=<generated-secret-key>
DATABASE_URL=<railway-postgres-url>
ALLOWED_HOSTS=bytes-backend-production.up.railway.app
```

### Railway Deployment Steps

1. Push code to GitHub repository
2. Connect Railway to GitHub repo
3. Configure environment variables in Railway dashboard
4. Railway auto-deploys on push to main branch
5. Run migrations: `python manage.py migrate`

---

## 📁 Project Structure

```
bytes-backend/
├── main_app/                   # Main Django application
│   ├── migrations/             # Database migrations
│   ├── models.py               # Recipe, Ingredient, Step, GroceryListItem models
│   ├── serializers.py          # DRF serializers with custom validation
│   ├── views.py                # API views and OpenAI integration
│   ├── urls.py                 # App-level URL routing
│   ├── validators.py           # Custom password validators
│   └── admin.py                # Django admin configuration
├── recipecollector/            # Django project settings
│   ├── settings.py             # Main configuration file
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py                 # WSGI application entry point
│   └── sendgrid_backend.py     # Custom SendGrid email backend
├── manage.py                   # Django management script
├── Pipfile                     # Python dependencies (pipenv)
├── Pipfile.lock                # Locked dependency versions
├── requirements.txt            # Pip requirements (for Railway)
├── start.sh                    # Production startup script
├── db.sqlite3                  # SQLite database (development)
└── README.md                   # This file
```

---

## 🧪 Key Technical Implementations

### AI Recipe Generation Flow

1. User sends prompt + optional dietary tags + optional grocery list flag
2. Backend constructs OpenAI system prompt with dietary constraints
3. If grocery list requested, includes checked items in prompt
4. OpenAI GPT-4o-mini generates structured JSON response
5. Backend normalizes units and validates structure
6. Returns recipe preview to frontend for user approval
7. User can save, edit, or regenerate

### Grocery List Smart Merging

1. User adds item (manually or from recipe)
2. Backend checks for existing item with same name
3. If found, determines measurement type (volume/weight/count)
4. Converts units to common base (ml for volume, g for weight)
5. Combines quantities and converts back to appropriate unit
6. Updates existing item or creates new one

### Image Upload & Storage

1. Frontend sends multipart form data (image + JSON)
2. Serializer extracts and validates image
3. Custom upload path function generates unique S3 key: `recipes/user_{id}/{uuid}.{ext}`
4. Boto3 uploads to S3 with cache headers
5. On retrieval, serializer generates presigned URL (24hr expiry)
6. On update/delete, old image automatically removed from S3

### Password Reset Flow

1. User requests reset with email address
2. Backend generates UID + token (1hr expiry)
3. SendGrid sends email with reset link: `{FRONTEND_URL}/reset-password?uid={uid}&token={token}`
4. User clicks link, enters new password
5. Frontend sends UID, token, new password to confirm endpoint
6. Backend validates token, updates password
7. User can log in with new password

---

## ✍️ Editor's Note

> The **Bytes.AI Backend** is the engine that powers a smarter way to cook — blending creativity, collaboration, and AI (At this day and age, what doesn't).
> This project reflects our shared goal of building technology that feels **helpful, elegant, and human**.
> From scalable Django architecture to AI-driven recipe generation, every component was crafted with care, curiosity, and hunger.

---

## 🔮 Future Enhancements

Potential next steps to expand **Bytes.AI**:

- **External MCP Server** - Implement a dedicated Model Context Protocol server for enhanced AI capabilities
- **Recipe Scaling** - Automatically adjust ingredient quantities for different serving sizes
- **Meal Planning** - Weekly meal planner with automatic grocery list generation
- **Nutrition Tracking** - Detailed macro and calorie tracking per recipe and meal
- **Social Features** - Share recipes with friends, public recipe discovery
- **Recipe Import** - Parse recipes from URLs or images using OCR
- **Shopping List Categorization** - Group items by store section (produce, dairy, etc.)
- **Voice Commands** - Hands-free cooking mode with step-by-step voice guidance
- **Recipe Rating & Reviews** - Community feedback system
- **Multi-language Support** - Internationalization for global users

---

## 👥 Contributors

| Name                                                | Role                                       |
| --------------------------------------------------- | ------------------------------------------ |
| **[Daniel Amit](https://github.com/DanielAmit217)** | Project Manager · Full-Stack & AI Engineer |
| **[Sara Mattina](https://github.com/saramattina)**  | Back-End Engineer · Repository Owner       |
| **[Dylan Tai](https://github.com/DylanTai)**        | Front-End Engineer · Repository Owner      |

> 💡 _Team Bytes.AI — fueled by innovation, caffeine, and clean commits._
