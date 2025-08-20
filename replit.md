# CivilAI Assistant

## Overview

CivilAI Assistant is a comprehensive web application designed for civil engineers, construction professionals, and students. The platform provides AI-powered assistance for structural design calculations, material estimation, project scheduling, and site safety analysis. Built with Flask and integrated with OpenAI's GPT-4o model, it offers intelligent responses to civil engineering queries while providing automated calculations based on established engineering practices and Indian Standard (IS) codes.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
- **Framework**: Flask-based web application with modular route organization
- **Entry Point**: `main.py` serves as the application runner, while `app.py` contains the Flask app configuration
- **Session Management**: Uses Flask sessions with configurable secret key for maintaining chat history and user state
- **Template Engine**: Jinja2 templating with a base template structure for consistent UI across pages

### AI Integration Layer
- **AI Service**: CivilAI class (`civil_ai.py`) manages OpenAI API interactions with specialized civil engineering context
- **Model Configuration**: Uses GPT-4o model with custom system prompts for civil engineering expertise
- **Error Handling**: Comprehensive logging and exception handling for API failures
- **Context Specialization**: System prompt specifically tuned for structural design, IS codes, materials, and construction practices

### Engineering Calculation Modules
- **Structural Calculator**: Beam design calculations including moment analysis, reinforcement requirements, and material properties
- **Material Estimator**: Bill of Quantities (BOQ) generation for construction projects
- **Project Scheduler**: Timeline planning with Gantt chart functionality
- **Material Database**: Predefined concrete grades (M15-M35) and steel grades (Fe415-Fe550) with properties

### Frontend Architecture
- **UI Framework**: Bootstrap with dark theme optimization for Replit environment
- **Component Structure**: Modular HTML templates with consistent navigation and styling
- **Interactive Features**: File upload handling, form validation, and real-time chat interface
- **Responsive Design**: Mobile-friendly layout with Font Awesome icons for enhanced UX

### File Upload System
- **Upload Handler**: Secure file handling with type validation and size limits (16MB max)
- **Supported Formats**: Image files (PNG, JPG, JPEG, GIF, BMP) for safety analysis
- **Security**: Werkzeug secure filename utility for safe file processing

### Route Organization
- **Modular Routing**: Separate routes file for clean separation of concerns
- **RESTful Design**: GET/POST method handling for different functionalities
- **Feature Pages**: Dedicated routes for chat, calculator, estimation, scheduler, and safety analysis

## External Dependencies

### AI Services
- **OpenAI API**: GPT-4o model for intelligent civil engineering responses
- **API Key Management**: Environment variable-based configuration for secure API access

### Python Libraries
- **Flask**: Web framework for application structure and routing
- **Werkzeug**: Secure file upload utilities and WSGI functionality
- **OpenAI Python SDK**: Official client library for OpenAI API integration

### Frontend Dependencies
- **Bootstrap**: CSS framework with dark theme support from Replit CDN
- **Font Awesome**: Icon library for enhanced visual interface
- **JavaScript**: Custom application logic for form handling and UI interactions

### Development Environment
- **Replit Platform**: Configured for direct execution with `python main.py`
- **Environment Variables**: Secure configuration management for API keys and secrets
- **Logging System**: Python logging module for debugging and error tracking

### File System Dependencies
- **Static Assets**: CSS and JavaScript files served through Flask's static file handling
- **Upload Directory**: Local file storage for uploaded images and documents
- **Template Directory**: Jinja2 template files for consistent page rendering