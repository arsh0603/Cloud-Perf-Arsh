# Firstprj-A

A full-stack application combining Django backend and React frontend.

## Project Structure

```
firstprj-a/
├── firstitr/          # Django backend application
│   ├── manage.py
│   ├── firstitr/      # Django project settings
│   └── myapp/         # Django app with cache management
└── my-react-app/      # React frontend application
    ├── src/
    ├── public/
    └── package.json
```

## Technologies Used

- **Backend**: Django (Python)
- **Frontend**: React (JavaScript)
- **Database**: SQLite (default Django database)

## Features

- Django backend with cache management functionality
- React frontend application
- RESTful API integration between frontend and backend

## Getting Started

### Prerequisites

- Python 3.x
- Node.js and npm
- Git

### Backend Setup (Django)

1. Navigate to the Django project:
   ```bash
   cd firstitr
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install django
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup (React)

1. Navigate to the React app:
   ```bash
   cd my-react-app
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

## Usage

- Django backend runs on `http://localhost:8000`
- React frontend runs on `http://localhost:3000`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).
