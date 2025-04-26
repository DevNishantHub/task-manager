# Task Manager Application

A comprehensive task management application with a Flask backend and React+TypeScript frontend. Manage tasks, notes, and categories with a modern, responsive interface.

## Features

- **Dashboard**: Visual overview of task completion rates and statistics
- **Task Management**: Create, edit, delete, filter, and sort tasks
- **Notes System**: Maintain a collection of notes with custom colors
- **Categories**: Organize tasks with custom color-coded categories
- **Responsive Design**: Works on both desktop and mobile devices

## Tech Stack

### Backend
- Flask (Python)
- Flask-CORS for cross-origin requests
- JSON-based data storage

### Frontend
- React with TypeScript
- Tailwind CSS for styling
- Chart.js for data visualization
- date-fns for date handling

## Getting Started

### Prerequisites

- Python 3.6+
- Node.js 14+ and npm

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/DevNishantHub/task-manager.git
   cd task-manager
   ```

2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```
   cd ../frontend
   npm install
   ```

### Running the Application

1. Start the backend server:
   ```
   cd backend
   python app.py
   ```
   The API will be available at http://localhost:5000

2. In a new terminal, start the frontend development server:
   ```
   cd frontend
   npm start
   ```
   The application will open in your default browser at http://localhost:3000

## API Endpoints

### Tasks
- `GET /api/tasks` - Get all tasks (with optional filtering and sorting)
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/:id` - Get a specific task
- `PUT /api/tasks/:id` - Update a task
- `DELETE /api/tasks/:id` - Delete a task
- `DELETE /api/tasks/bulk` - Delete multiple tasks

### Notes
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create a new note
- `GET /api/notes/:id` - Get a specific note
- `PUT /api/notes/:id` - Update a note
- `DELETE /api/notes/:id` - Delete a note

### Categories
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create a new category
- `PUT /api/categories/:id` - Update a category
- `DELETE /api/categories/:id` - Delete a category

### Statistics
- `GET /api/stats` - Get application statistics

## Project Structure

```
task-manager/
├── backend/                # Flask backend
│   ├── app.py              # Main application file
│   ├── requirements.txt    # Python dependencies
│   ├── tasks.json          # Tasks data storage
│   ├── notes.json          # Notes data storage
│   └── categories.json     # Categories data storage
│
└── frontend/               # React frontend
    ├── public/             # Static files
    └── src/                # Source files
        ├── components/     # React components
        ├── services/       # API services
        ├── types.ts        # TypeScript interfaces
        └── App.tsx         # Main application component
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- All the open-source libraries that made this project possible
- Inspiration from popular task management applications