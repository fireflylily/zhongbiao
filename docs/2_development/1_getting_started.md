# Getting Started with Development

This guide provides instructions for setting up the development environment for both the backend and frontend of the AI-Tender-System.

## Backend Development (Python/Flask)

### Prerequisites

- **Python**: 3.11 or higher

### Setup

1.  **Install Dependencies**:
    It is recommended to use a virtual environment.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    pip install -r requirements-dev.txt # For development tools
    ```

2.  **Configure Environment**:
    Copy the example environment file and fill in your details.

    ```bash
    cp ai_tender_system/.env.example ai_tender_system/.env
    ```

    Edit `.env` to add your API keys and set `DEBUG=True`.

3.  **Initialize Database**:

    ```bash
    python -m ai_tender_system.database.init_db
    ```

4.  **Run the Backend Server**:

    ```bash
    export FLASK_ENV=development
    export DEBUG=True
    python -m ai_tender_system.web.app
    ```

    The backend server will be running at `http://localhost:5000`.

## Frontend Development (Vue.js)

### Prerequisites

- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher

### Setup

1.  **Navigate to Frontend Directory**:

    ```bash
    cd frontend
    ```

2.  **Install Dependencies**:

    ```bash
    npm install
    ```

3.  **Run the Frontend Development Server**:

    ```bash
    npm run dev
    ```

    The frontend development server will be running at `http://localhost:5173`. It will automatically proxy API requests to the backend server running on `http://localhost:8110` (as configured in `vite.config.ts`).

    **Note**: Ensure your backend is configured to run on port 8110 if you are using the default frontend proxy configuration.

### Building for Production

To build the frontend for production, run:

```bash
npm run build
```

The output will be placed in `ai_tender_system/web/static/dist/`, which is served by the Flask backend in production.
