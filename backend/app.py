from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import os
import uuid
from werkzeug.exceptions import BadRequest, NotFound
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File paths for storing data
TASKS_FILE = 'tasks.json'
NOTES_FILE = 'notes.json'
CATEGORIES_FILE = 'categories.json'

# Default categories
DEFAULT_CATEGORIES = [
    {"id": 1, "name": "Work", "color": "#3b82f6"},
    {"id": 2, "name": "Personal", "color": "#10b981"},
    {"id": 3, "name": "Shopping", "color": "#f59e0b"},
    {"id": 4, "name": "Health", "color": "#ef4444"},
    {"id": 5, "name": "Education", "color": "#8b5cf6"}
]

# Helper functions to read and write data
def read_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error reading data from {file_path}: {e}")
        return []

def write_data(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error writing data to {file_path}: {e}")
        return False

def validate_task(task):
    """Validate task data"""
    errors = []
    if not task.get('title'):
        errors.append("Title is required")
    if 'completed' not in task:
        errors.append("Completed status is required")
    return errors

def validate_note(note):
    """Validate note data"""
    errors = []
    if not note.get('title'):
        errors.append("Title is required")
    return errors

# Error handler for 404 errors
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

# Error handler for 400 errors
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400

# Error handler for all other exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify(error="An unexpected error occurred"), 500

# Routes for tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering and sorting"""
    tasks = read_data(TASKS_FILE)
    
    # Filter by query parameter if provided
    query = request.args.get('query', '').lower()
    if query:
        tasks = [task for task in tasks if query in task.get('title', '').lower()]
    
    # Filter by status if provided
    status = request.args.get('status')
    if status == 'completed':
        tasks = [task for task in tasks if task.get('completed')]
    elif status == 'active':
        tasks = [task for task in tasks if not task.get('completed')]
    
    # Filter by category if provided
    category_id = request.args.get('category_id')
    if category_id and category_id.isdigit():
        category_id = int(category_id)
        tasks = [task for task in tasks if task.get('category_id') == category_id]
    
    # Sort by parameter if provided
    sort_by = request.args.get('sort_by', 'created_at')
    reverse = request.args.get('order', 'desc').lower() == 'desc'
    
    if sort_by == 'title':
        tasks = sorted(tasks, key=lambda x: x.get('title', '').lower(), reverse=reverse)
    elif sort_by == 'due_date':
        tasks = sorted(tasks, key=lambda x: x.get('due_date', ''), reverse=reverse)
    else:  # default sort by created_at
        tasks = sorted(tasks, key=lambda x: x.get('created_at', ''), reverse=reverse)
    
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add a new task"""
    try:
        task = request.json
        if not task:
            raise BadRequest("No task data provided")
        
        # Validate task
        errors = validate_task(task)
        if errors:
            return jsonify({"error": "Invalid task data", "details": errors}), 400
        
        tasks = read_data(TASKS_FILE)
        
        # Add ID if not provided
        if 'id' not in task:
            task['id'] = max([t.get('id', 0) for t in tasks], default=0) + 1
        
        # Add timestamps
        current_time = datetime.now().isoformat()
        task['created_at'] = current_time
        task['updated_at'] = current_time
        
        # Add default priority if not provided
        if 'priority' not in task:
            task['priority'] = 'medium'
            
        tasks.append(task)
        write_data(TASKS_FILE, tasks)
        return jsonify(task), 201
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return jsonify({"error": "Failed to add task"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    tasks = read_data(TASKS_FILE)
    
    for task in tasks:
        if task.get('id') == task_id:
            return jsonify(task)
    
    raise NotFound(f"Task with ID {task_id} not found")

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task by ID"""
    try:
        task_data = request.json
        if not task_data:
            raise BadRequest("No task data provided")
        
        tasks = read_data(TASKS_FILE)
        
        for i, task in enumerate(tasks):
            if task.get('id') == task_id:
                # Update task but preserve ID and creation date
                task_data['id'] = task_id
                task_data['created_at'] = task.get('created_at')
                task_data['updated_at'] = datetime.now().isoformat()
                
                tasks[i] = task_data
                write_data(TASKS_FILE, tasks)
                return jsonify(task_data)
        
        raise NotFound(f"Task with ID {task_id} not found")
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return jsonify({"error": f"Failed to update task {task_id}"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task by ID"""
    try:
        tasks = read_data(TASKS_FILE)
        
        for i, task in enumerate(tasks):
            if task.get('id') == task_id:
                del tasks[i]
                write_data(TASKS_FILE, tasks)
                return jsonify({"message": f"Task {task_id} deleted successfully"})
        
        raise NotFound(f"Task with ID {task_id} not found")
    
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return jsonify({"error": f"Failed to delete task {task_id}"}), 500

@app.route('/api/tasks/bulk', methods=['DELETE'])
def bulk_delete_tasks():
    """Delete multiple tasks at once"""
    try:
        data = request.json
        if not data or 'ids' not in data or not isinstance(data['ids'], list):
            raise BadRequest("Invalid request: 'ids' list is required")
        
        task_ids = data['ids']
        tasks = read_data(TASKS_FILE)
        
        # Find indices of tasks to delete (in reverse order to avoid shifting indices)
        indices_to_delete = [i for i, task in enumerate(tasks) if task.get('id') in task_ids]
        indices_to_delete.sort(reverse=True)
        
        # Delete the tasks
        deleted_count = 0
        for i in indices_to_delete:
            del tasks[i]
            deleted_count += 1
        
        # Write updated tasks
        write_data(TASKS_FILE, tasks)
        
        return jsonify({
            "message": f"Deleted {deleted_count} tasks successfully",
            "deleted_count": deleted_count
        })
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error bulk deleting tasks: {e}")
        return jsonify({"error": "Failed to delete tasks"}), 500

# Routes for notes
@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get all notes with optional filtering and sorting"""
    notes = read_data(NOTES_FILE)
    
    # Filter by query parameter if provided
    query = request.args.get('query', '').lower()
    if query:
        notes = [
            note for note in notes 
            if query in note.get('title', '').lower() or query in note.get('content', '').lower()
        ]
    
    # Sort by parameter if provided
    sort_by = request.args.get('sort_by', 'created_at')
    reverse = request.args.get('order', 'desc').lower() == 'desc'
    
    if sort_by == 'title':
        notes = sorted(notes, key=lambda x: x.get('title', '').lower(), reverse=reverse)
    else:  # default sort by created_at
        notes = sorted(notes, key=lambda x: x.get('created_at', ''), reverse=reverse)
    
    return jsonify(notes)

@app.route('/api/notes', methods=['POST'])
def add_note():
    """Add a new note"""
    try:
        note = request.json
        if not note:
            raise BadRequest("No note data provided")
        
        # Validate note
        errors = validate_note(note)
        if errors:
            return jsonify({"error": "Invalid note data", "details": errors}), 400
        
        notes = read_data(NOTES_FILE)
        
        # Add ID if not provided
        if 'id' not in note:
            note['id'] = max([n.get('id', 0) for n in notes], default=0) + 1
        
        # Add timestamps
        current_time = datetime.now().isoformat()
        note['created_at'] = current_time
        note['updated_at'] = current_time
        
        notes.append(note)
        write_data(NOTES_FILE, notes)
        return jsonify(note), 201
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        return jsonify({"error": "Failed to add note"}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    notes = read_data(NOTES_FILE)
    
    for note in notes:
        if note.get('id') == note_id:
            return jsonify(note)
    
    raise NotFound(f"Note with ID {note_id} not found")

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note by ID"""
    try:
        note_data = request.json
        if not note_data:
            raise BadRequest("No note data provided")
        
        notes = read_data(NOTES_FILE)
        
        for i, note in enumerate(notes):
            if note.get('id') == note_id:
                # Update note but preserve ID and creation date
                note_data['id'] = note_id
                note_data['created_at'] = note.get('created_at')
                note_data['updated_at'] = datetime.now().isoformat()
                
                notes[i] = note_data
                write_data(NOTES_FILE, notes)
                return jsonify(note_data)
        
        raise NotFound(f"Note with ID {note_id} not found")
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating note {note_id}: {e}")
        return jsonify({"error": f"Failed to update note {note_id}"}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note by ID"""
    try:
        notes = read_data(NOTES_FILE)
        
        for i, note in enumerate(notes):
            if note.get('id') == note_id:
                del notes[i]
                write_data(NOTES_FILE, notes)
                return jsonify({"message": f"Note {note_id} deleted successfully"})
        
        raise NotFound(f"Note with ID {note_id} not found")
    
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}")
        return jsonify({"error": f"Failed to delete note {note_id}"}), 500

# Routes for categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = read_data(CATEGORIES_FILE)
    return jsonify(categories)

@app.route('/api/categories', methods=['POST'])
def add_category():
    """Add a new category"""
    try:
        category = request.json
        if not category or 'name' not in category:
            raise BadRequest("Category name is required")
        
        categories = read_data(CATEGORIES_FILE)
        
        # Add ID if not provided
        if 'id' not in category:
            category['id'] = max([c.get('id', 0) for c in categories], default=0) + 1
        
        # Set default color if not provided
        if 'color' not in category:
            category['color'] = "#" + uuid.uuid4().hex[:6]  # Random color
        
        categories.append(category)
        write_data(CATEGORIES_FILE, categories)
        return jsonify(category), 201
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding category: {e}")
        return jsonify({"error": "Failed to add category"}), 500

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update a category by ID"""
    try:
        category_data = request.json
        if not category_data or 'name' not in category_data:
            raise BadRequest("Category name is required")
        
        categories = read_data(CATEGORIES_FILE)
        
        for i, category in enumerate(categories):
            if category.get('id') == category_id:
                # Update category but preserve ID
                category_data['id'] = category_id
                categories[i] = category_data
                write_data(CATEGORIES_FILE, categories)
                return jsonify(category_data)
        
        raise NotFound(f"Category with ID {category_id} not found")
    
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {e}")
        return jsonify({"error": f"Failed to update category {category_id}"}), 500

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category by ID"""
    try:
        categories = read_data(CATEGORIES_FILE)
        
        for i, category in enumerate(categories):
            if category.get('id') == category_id:
                del categories[i]
                write_data(CATEGORIES_FILE, categories)
                return jsonify({"message": f"Category {category_id} deleted successfully"})
        
        raise NotFound(f"Category with ID {category_id} not found")
    
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {e}")
        return jsonify({"error": f"Failed to delete category {category_id}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    tasks = read_data(TASKS_FILE)
    notes = read_data(NOTES_FILE)
    
    # Calculate task statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.get('completed'))
    pending_tasks = total_tasks - completed_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Group tasks by category
    category_counts = {}
    for task in tasks:
        category_id = task.get('category_id')
        if category_id:
            category_counts[category_id] = category_counts.get(category_id, 0) + 1
    
    # Calculate note statistics
    total_notes = len(notes)
    
    return jsonify({
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks,
            "completion_rate": round(completion_rate, 2),
            "by_category": category_counts
        },
        "notes": {
            "total": total_notes
        }
    })

if __name__ == '__main__':
    # Create empty data files if they don't exist
    if not os.path.exists(TASKS_FILE):
        write_data(TASKS_FILE, [])
    if not os.path.exists(NOTES_FILE):
        write_data(NOTES_FILE, [])
    if not os.path.exists(CATEGORIES_FILE):
        write_data(CATEGORIES_FILE, DEFAULT_CATEGORIES)
    
    logger.info("Starting Task Manager API server")
    app.run(debug=True)