# FoodVerse-AI — Food Intelligence & Nutrition Platform

FoodVerse-AI is an end-to-end full-stack nutrition intelligence and food recommendation system. It integrates computer vision, heuristic nutritional scoring, dietary calibration algorithms, persistent MySQL / SQLite database storage via SQLAlchemy, and a modern health-tech React dashboard.

---

## 🚀 Key Features

1. **Food Discovery & Catalog**: Search nutrient-dense recipes and dishes with filtering by meal category (Breakfast, Lunch, Dinner, Snack, Salad, Beverage) and diet type (Vegan, Vegetarian, Eggetarian, Non-Vegetarian). Features 1-click meal logging and custom dish creation.
2. **Food Recognition & Nutrition Estimation**: Inspect food photographs to calculate estimated macronutrients (calories, protein, carbohydrates, fats, fiber), compute a 0–100 health score, and automatically persist analyses into the database.
3. **Personalized Food Recommendations**: Calculates tailored daily caloric targets and macronutrient distributions from age, height, weight, activity level, and fitness goals (caloric deficit, maintenance, muscle gain), returning compatible meals.
4. **Calibrated Meal Planner**: Generates daily multi-meal plans with automated portion scaling, target comparison, and database saving.
5. **Food Intake Logs & Nutrition Analytics**: Real-time daily progress trackers for calories and macros, macronutrient distribution charts, and persistent food intake history.
6. **Freshness & Hygiene Evaluation**: Visual indicators of food freshness and kitchen hygiene observations with food-safety guidance.
7. **Smart Kitchen Assistant**: Ingredient-based recipe generator providing step-by-step cooking instructions, prep time, and safety notes.
8. **Analysis History**: Browse, search, and manage persistent historical meal scans stored in the database.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+ / 3.14, FastAPI, Pydantic v2, Uvicorn, Python-Dotenv, Pillow, OpenCV Headless.
- **Database & ORM**: SQLAlchemy 2.0 ORM, PyMySQL (for MySQL), SQLite (for safe local development fallback).
- **Frontend**: React 19, Vite 8, Lucide React icons, Recharts visualization library.
- **APIs & AI**: FastAPI REST API, Groq Vision / LLM API (optional for live AI image assessment).

---

## 📁 Project Structure

```text
food/
├── .venv/                                   # Python virtual environment
├── README.md                                # Comprehensive documentation
├── 5.Projects development Phase/
│   ├── backend/
│   │   ├── main.py                          # FastAPI application and route registration
│   │   ├── database.py                      # SQLAlchemy engine, session management, safe fallback
│   │   ├── models.py                        # Declarative ORM models (Users, Foods, Logs, Plans, etc.)
│   │   ├── create_tables.py                 # Table initialization & initial food catalog seeding
│   │   ├── test_database.py                 # Database CRUD test suite
│   │   ├── test_api.py                      # FastAPI endpoint test suite
│   │   ├── requirements.txt                 # Backend Python dependencies
│   │   ├── .env.example                     # Environment template for MySQL & keys
│   │   ├── .env                             # Local environment configuration
│   │   ├── routers/
│   │   │   ├── food_items.py                # Food catalog CRUD & search
│   │   │   ├── recommendations.py           # Personalized meal recommendation engine
│   │   │   ├── meal_plans.py                # Daily meal plan persistence
│   │   │   ├── food_logs.py                 # Meal intake logging & daily analytics
│   │   │   ├── database.py                  # Preserved analyses & stats endpoints
│   │   │   ├── meal_planner.py              # Profile validation & portion scaling
│   │   │   ├── nutrition.py                 # Vision-based nutrition estimation
│   │   │   ├── nutrition_scoring.py         # Heuristic health score formula
│   │   │   ├── food_recognition.py          # Vision food recognition
│   │   │   ├── freshness.py                 # Food freshness assessment
│   │   │   ├── hygiene_monitor.py           # Kitchen hygiene monitor
│   │   │   └── kitchen_assistant.py         # Smart kitchen recipe generation
│   │   └── services/
│   │       ├── meal_recommendation.py       # Recommendation rules & catalog
│   │       ├── image_preprocessing.py       # OpenCV image feature extractor
│   │       └── video_processing.py          # Video frame extraction
│   └── frontend/
│       ├── package.json                     # Frontend dependencies
│       ├── vite.config.js                   # Vite configuration
│       ├── .env.example                     # Frontend environment template
│       ├── .env                             # VITE_API_BASE_URL=http://localhost:8000
│       ├── index.html                       # Application entry point
│       └── src/
│           ├── main.jsx                     # React root mount
│           ├── App.jsx                      # Full-stack integrated dashboard & modules
│           ├── App.css                      # Modern component styling
│           ├── index.css                    # Design tokens, typography & dark theme
│           └── services/
│               └── api.js                   # Centralized API client for all backend endpoints
```

---

## 🗄️ Database Architecture & Entities

The database layer utilizes SQLAlchemy ORM with support for both **MySQL (PyMySQL)** and a safe **SQLite local development fallback**:

1. **`users`**: User identifiers, credentials (`hashed_password`), profile attributes, and active status.
2. **`food_items`**: Verified nutrient-dense food catalog (`name`, `category`, `cuisine`, `diet_type`, `calories_kcal`, `protein_g`, `carbs_g`, `fat_g`, `fiber_g`, `serving_size_g`, `allergens`, `ingredients`).
3. **`user_profiles`**: User physical attributes (`age`, `height_cm`, `weight_kg`, `activity_level`, `goal`, `dietary_preference`, `allergies`, `disliked_foods`, `meals_per_day`).
4. **`food_recommendations`**: Generated personalized recommendations (`goal`, `target_calories_kcal`, `target_macros`, `recommended_items`, `reasoning`, `health_score`).
5. **`meal_plans`**: Saved daily meal schedules (`plan_name`, `target_calories_kcal`, `planned_calories_kcal`, `meals_data`, `nutrition_summary`, `notes`).
6. **`food_logs`**: Recorded daily meal intake (`dish_name`, `meal_type`, `portion_weight_g`, `calories_kcal`, `protein_g`, `carbs_g`, `fat_g`, `health_score`, `logged_at`).
7. **`meal_analyses`**: Preserved AI food recognition and estimated nutrition history.

---

## ⚙️ Prerequisites & Setup

### 1. Prerequisites
- Python 3.12+ or 3.14 with `pip`
- Node.js 18+ and `npm`
- MySQL Server 8.0+ (Optional: If MySQL is not running, the application automatically uses SQLite safe fallback)

### 2. MySQL Setup (Optional, Primary Production Target)
If using MySQL, start the MySQL server and create the database:
```sql
CREATE DATABASE foodverse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Configure `5.Projects development Phase/backend/.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=foodverse
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_FALLBACK_SQLITE=true
GROQ_API_KEY=your_optional_groq_api_key
```

*Note:* If MySQL credentials are not supplied or MySQL is offline, `database.py` safely switches to local SQLite (`foodverse.db`) without throwing errors.

---

## 💻 Running the Application

### Step 1: Initialize Database Tables & Seed Catalog
From the backend directory:
```powershell
cd "5.Projects development Phase\backend"
..\..\.venv\Scripts\python.exe create_tables.py
```
Or run the database verification test suite:
```powershell
..\..\.venv\Scripts\python.exe test_database.py
```

### Step 2: Run FastAPI Backend
```powershell
cd "5.Projects development Phase\backend"
..\..\.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Swagger Interactive Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Step 3: Run React Frontend
In a new terminal window:
```powershell
cd "5.Projects development Phase\frontend"
npm run dev
```
- Frontend UI: `http://localhost:5173`

---

## 🧪 Testing

### Backend Unit & Integration Tests
Run the API endpoint test suite:
```powershell
cd "5.Projects development Phase\backend"
..\..\.venv\Scripts\python.exe test_api.py
```
*Result: Verifies all 12 core API routes (health, food-items, categories, search, recommendations, meal-plans, food-logs, database stats, and meal planner).*

### Frontend Production Build Test
Verify the React bundle compiles without errors:
```powershell
cd "5.Projects development Phase\frontend"
npm run build
```
*Result: Built production distribution bundle with zero warnings or errors.*

---

## 🔍 Troubleshooting

1. **Database connection failed / MySQL port 3306 not open:**
   - The application automatically falls back to local SQLite (`foodverse.db`) with zero downtime.
   - To connect to MySQL, verify the MySQL service is started (`net start MySQL80` or MySQL Workbench) and your `.env` contains valid credentials.
2. **Missing `lucide-react` or `recharts`:**
   - Run `cd "5.Projects development Phase\frontend"` and `npm install`.
3. **CORS issues:**
   - FastAPI CORS middleware is already configured for `http://localhost:5173` and `http://127.0.0.1:5173`.
4. **Groq Vision API:**
   - Image recognition works with a free key from `console.groq.com`. If no key is set, the Food Discovery and Meal Planner modules still function seamlessly with heuristic calculations.

