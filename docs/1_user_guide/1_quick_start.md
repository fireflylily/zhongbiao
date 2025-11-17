# Quick Start

This guide will help you get the AI-Tender-System up and running on your local machine.

## Environment Requirements

- **Python**: 3.11 or higher
- **OS**: Windows / macOS / Linux
- **Memory**: 8GB+ recommended
- **Disk Space**: 2GB+ (for models and dependencies)

## Installation Steps

### 1. Clone the Project

```bash
git clone <repository-url>
cd zhongbiao
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp ai_tender_system/.env.example ai_tender_system/.env
```

Edit the `.env` file to add your API keys:

```ini
# AI Model Configuration
QWEN_API_KEY=your_qwen_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional
DEEPSEEK_API_KEY=your_deepseek_api_key_here  # Optional

# Application Configuration
SECRET_KEY=your_secret_key_for_csrf_protection
DEBUG=False
```

### 4. Initialize the Database

```bash
python -m ai_tender_system.database.init_db
```

### 5. Start the Application

```bash
python -m ai_tender_system.web.app
```

### 6. Access the System

Open your browser and go to: [http://localhost:5000](http://localhost:5000)

**Default Login:**
- **Username:** `admin`
- **Password:** `admin123`

**Security Warning:** Please change the default password immediately after your first login!
