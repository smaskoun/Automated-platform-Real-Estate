# Copilot Instructions for Automated Platform Real Estate

## Overview
This platform is a full-stack application for managing real estate-related content, including brand voices, SEO tools, and social media automation. It consists of a Flask-based backend and a React-based frontend.

### Key Components
1. **Backend**:
   - Built with Flask.
   - Organized into modular blueprints for features like brand voices, SEO tools, and social media.
   - Database managed using SQLAlchemy and Alembic for migrations.
   - Key directories:
     - `src/routes/`: API endpoints.
     - `src/models/`: Database schema.
     - `src/services/`: Business logic and integrations.

2. **Frontend**:
   - Built with React and Vite.
   - Tailwind CSS for styling.
   - Key files:
     - `frontend/src/App.jsx`: Main application component.
     - `frontend/src/api.js`: API integration.

### Data Flow
- **Frontend**: Sends API requests to the backend for CRUD operations.
- **Backend**: Processes requests, interacts with the database, and returns JSON responses.

## Developer Workflows

### Backend
1. **Run the Application**:
   ```bash
   python src/main.py
   ```
2. **Database Migrations**:
   - Generate a migration:
     ```bash
     flask db migrate -m "Migration message"
     ```
   - Apply migrations:
     ```bash
     flask db upgrade
     ```

3. **Run Tests**:
   ```bash
   pytest tests/
   ```

### Frontend
1. **Install Dependencies**:
   ```bash
   npm install
   ```
2. **Run the Development Server**:
   ```bash
   npm run dev
   ```
3. **Build for Production**:
   ```bash
   npm run build
   ```

## Project-Specific Conventions
1. **Blueprints**:
   - Each feature has its own blueprint in `src/routes/`.
   - Example: `brand_voice_routes.py` for brand voice management.

2. **Models**:
   - Defined in `src/models/`.
   - Example: `BrandVoice` model includes fields like `name`, `description`, and `post_example`.

3. **Error Handling**:
   - Use `try-except` blocks for database operations.
   - Log errors using Python's `logging` module.

## Integration Points
1. **Frontend-Backend Communication**:
   - API endpoints are defined in `src/routes/`.
   - Example: `POST /api/brand-voices` to create a brand voice.

2. **Database**:
   - Managed with SQLAlchemy models in `src/models/`.
   - Migrations handled using Alembic.

3. **Services**:
   - Business logic is encapsulated in `src/services/`.
   - Example: `SEOContentService` for SEO-related operations.

## Examples
1. **Add a New Route**:
   - Create a new file in `src/routes/`.
   - Define a `Blueprint` and register it in `src/main.py`.

2. **Add a New Model**:
   - Create a new file in `src/models/`.
   - Define a SQLAlchemy model and add it to the database.

3. **Extend Frontend**:
   - Add a new component in `frontend/src/`.
   - Use `api.js` to integrate with the backend.

---

For further questions, refer to the `README.md` or contact the project maintainers.