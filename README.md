![alt text](./images/image%20copy.png)

# 🍔 Bytes.AI Backend

The backend for **Bytes.AI**, A straightforward recipe managment app, with an intelligent recipe generation platform that blends creative AI with smart grocery list management.  
Built with **Django**, powered by **OpenAI**, and deployed on **Railway**.

---

## 🍜 Overview

The Bytes.AI backend provides the core API and business logic for the app.
It handles:

- AI-powered recipe generation using OpenAI’s API
- Secure image storage via AWS S3
- Persistent user data and grocery management through Django models
- Communication with the MCP (Model Context Protocol) server for local AI requests

This service powers all frontend interactions, exposing RESTful endpoints and managing authentication, data persistence, and external integrations.

---

## 🧑‍💻 Technologies Used

| Technology                       | Purpose                                       |
| -------------------------------- | --------------------------------------------- |
| **Django**                       | Core backend framework                        |
| **Django REST Framework (DRF)**  | REST API serialization and routing            |
| **OpenAI API**                   | AI recipe generation and contextual responses |
| **AWS S3**                       | Image and asset storage                       |
| **Railway**                      | Deployment and hosting                        |
| **MCP (Model Context Protocol)** | Local AI integration with OpenAI’s API        |
| **PostgreSQL**                   | Database for structured data                  |

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
- **pip**
- **PostgreSQL** (if running locally)

You’ll also need API keys for:

- OpenAI
- AWS S3
- Django SECRET_KEY

---

### ⚡ Local Setup

```bash
# 1️⃣ Clone the repository
git clone https://github.com/saramattina/bytes-backend
cd bytes-backend

# 2️⃣ Activate the Pipenv shell
pipenv shell

# 3️⃣ Install dependencies (this also creates a virtual environment)
pipenv install

# 4️⃣ Create your .env file from the example
touch .env
# Fill in your environment variables:
# OPENAI_API_KEY
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# AWS_STORAGE_BUCKET_NAME
# AWS_S3_REGION_NAMEDJANGO_ENV
# --- make sure to have this as well:
# DJANGO_ENV=development

# 5️⃣ Apply migrations
python manage.py migrate

# 6️⃣ Run the development server
python manage.py runserver
```

## ✍️ Editor’s Note

> The **Bytes.AI Backend** is the engine that powers a smarter way to cook — blending creativity, collaboration, and AI (At this day and age, what doesn't).  
> This project reflects our shared goal of building technology that feels **helpful, elegant, and human**.  
> From scalable Django architecture to AI-driven recipe generation, every component was crafted with care, curiosity, and hunger.

---

## Next Steps ➡️

Our next step would be to expand the AI functionality of **Bytes** by implementing an actual external **MCP** (Model Context Protocol) server. Currently, the app has moch MCP functionality locally. having an external server would allow us to further push the AI features of the app!

## 👥 Contributors

| Name                                                | Role                                       |
| --------------------------------------------------- | ------------------------------------------ |
| **[Daniel Amit](https://github.com/DanielAmit217)** | Project Manager · Full-Stack & AI Engineer |
| **[Sara Mattina](https://github.com/saramattina)**  | Front-End Engineer · Repository Owner      |
| **[Dylan Tai](https://github.com/DylanTai)**        | Back-End Engineer · Repository Owner       |

> 💡 _Team Bytes.AI — fueled by innovation, caffeine, and clean commits._
