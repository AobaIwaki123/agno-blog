# Agno Blog Application - Refactored Structure

This directory contains the refactored Agno Blog application with a clean, modular architecture.

## Directory Structure

```
src/
├── main.py                 # Main entry point (simplified)
├── config.py              # Application configuration
├── database.py            # Database initialization
├── logging_config.py      # Logging configuration
├── requirements.txt       # Python dependencies
├── agents/
│   ├── __init__.py
│   ├── factory.py         # Agent creation and management
│   ├── content_generator.py  # Content generation agent
│   ├── template_manager.py   # Template management agent
│   └── url_processor.py      # URL processing agent
├── models/
│   ├── __init__.py
│   ├── api.py            # API request/response models
│   └── blog_post.py      # Blog post data models
├── routers/
│   ├── __init__.py
│   ├── api.py           # REST API routes
│   └── web.py           # Web UI routes
├── tools/
│   ├── __init__.py
│   ├── content_processor.py  # Content processing tools
│   ├── template_manager.py   # Template management tools
│   └── web_scraper.py        # Web scraping tools
└── workflows/
    └── __init__.py
```

## Key Improvements

### 1. **Separation of Concerns**
- **Configuration**: Centralized in `config.py`
- **Database**: Isolated in `database.py`
- **Agents**: Factory pattern in `agents/factory.py`
- **API Routes**: Separated into `routers/api.py`
- **Web Routes**: Separated into `routers/web.py`
- **Logging**: Centralized in `logging_config.py`

### 2. **Clean Main Entry Point**
The new `main.py` is much simpler and focused only on:
- Application initialization
- Router registration
- Agent integration
- Application startup

### 3. **Modular Architecture**
- Each component has a single responsibility
- Easy to test individual components
- Better maintainability and readability
- Clear import structure

### 4. **Better Error Handling**
- Graceful degradation when agents fail to initialize
- Comprehensive logging throughout the application
- Proper exception handling in all modules

## Running the Application

```bash
# From the src directory
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

Make sure to set the required environment variables:

```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key
export OPENAI_API_KEY=your_openai_api_key
export CO_API_KEY=your_cohere_api_key  # Optional, for knowledge base
export DEBUG=true  # Optional, for development
```

## API Endpoints

- **Web UI**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Agent Interface**: http://localhost:8000/agno (when agents are available)
- **Health Check**: http://localhost:8000/api/health

## Benefits of This Structure

1. **Maintainability**: Each file has a clear purpose and is easier to understand
2. **Testability**: Components can be tested in isolation
3. **Scalability**: New features can be added without cluttering existing code
4. **Debugging**: Issues are easier to locate and fix
5. **Collaboration**: Multiple developers can work on different components simultaneously

## Migration Notes

The refactoring maintains full compatibility with the existing functionality while providing a much cleaner codebase for future development.
