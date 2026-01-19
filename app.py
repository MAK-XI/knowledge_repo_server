"""
Knowledge Repository - Flask Backend Server
SQLAlchemy ORM Version
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import config
from database import init_db, get_db, engine, Base
from routes import register_blueprints
from auth import admin_required

# Initialize Flask app
app = Flask(__name__, static_folder='..')
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Enable CORS
CORS(app)

# Register all API blueprints
register_blueprints(app)


# ==========================================
# Static File Serving
# ==========================================

@app.route('/')
@app.route('/index.html')
def serve_index():
    """Serve the main index.html."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/login.html')
def serve_login():
    """Serve the login page."""
    return send_from_directory(app.static_folder, 'login.html')


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files."""
    return send_from_directory(config.UPLOAD_FOLDER, filename)


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files."""
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files."""
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)


@app.route('/api-client.js')
def serve_api_client():
    """Serve the API client JavaScript."""
    return send_from_directory(app.static_folder, 'api-client.js')


@app.route('/favicon.ico')
def serve_favicon():
    """Serve favicon."""
    try:
        return send_from_directory(app.static_folder, 'favicon.ico')
    except:
        return '', 204


# ==========================================
# System Routes (Maintenance)
# ==========================================

@app.route('/api/admin/run-migration', methods=['GET'])
@admin_required
def run_migration():
    """Run database migrations (admin only)."""
    try:
        print('Running migration from web trigger...')
        # With SQLAlchemy, migrations are handled by create_all or Alembic
        # This endpoint now just ensures all tables exist
        Base.metadata.create_all(bind=engine)
        return jsonify({'success': True, 'message': 'Migration executed successfully'})
        
    except Exception as e:
        print(f'Migration error: {e}')
        return jsonify({'error': str(e)}), 500


# ==========================================
# Error Handlers
# ==========================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors - try to serve static files."""
    # Try to serve as a static file
    path = e.description if hasattr(e, 'description') else ''
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


def seed_default_data():
    """Seed default categories, departments, and priorities using SQLAlchemy."""
    from models.orm import Category, Department, Priority
    
    db = get_db()
    try:
        # Default categories
        categories = [
            ('הדרכה', 'מאמרי הדרכה והכשרה'),
            ('נהלים', 'נהלי עבודה ותקנון'),
            ('טכני', 'מידע טכני ותמיכה'),
            ('שירות לקוחות', 'מידע לנציגי שירות'),
            ('מכירות', 'חומרי מכירות ומידע מסחרי'),
            ('כללי', 'מידע כללי')
        ]
        for name, desc in categories:
            existing = db.query(Category).filter_by(name=name).first()
            if not existing:
                db.add(Category(name=name, description=desc))
        
        # Default departments
        departments = [
            ('תפעול', 'מחלקת תפעול'),
            ('פיתוח', 'מחלקת פיתוח תוכנה'),
            ('שיווק', 'מחלקת שיווק ופרסום'),
            ('משאבי אנוש', 'מחלקת משאבי אנוש'),
            ('הנהלה', 'הנהלת החברה'),
            ('תמיכה טכנית', 'מחלקת תמיכה טכנית')
        ]
        for name, desc in departments:
            existing = db.query(Department).filter_by(name=name).first()
            if not existing:
                db.add(Department(name=name, description=desc))
        
        # Default priorities
        priorities = [
            ('דחוף', 4, '#DC3545'),
            ('גבוהה', 3, '#E74C5C'),
            ('בינונית', 2, '#FFC107'),
            ('נמוכה', 1, '#28A745')
        ]
        for name, level, color in priorities:
            existing = db.query(Priority).filter_by(name=name).first()
            if not existing:
                db.add(Priority(name=name, level=level, color=color))
        
        db.commit()
        print('✅ Default data seeded successfully')
        
    except Exception as e:
        db.rollback()
        print(f'Error seeding data: {e}')
    finally:
        db.close()


# ==========================================
# Main Entry Point
# ==========================================

if __name__ == '__main__':
    # Ensure uploads directory exists
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    
    # Initialize database with SQLAlchemy
    try:
        init_db()
        seed_default_data()
    except Exception as e:
        print(f'Failed to initialize database: {e}')
    
    # Print startup banner
    port = config.PORT
    print(f"""
╔════════════════════════════════════════════════════════╗
║                                                        ║
║   Knowledge Repository Server (Flask/SQLAlchemy)       ║
║                                                        ║
║   Server running at: http://localhost:{port}             ║
║   API available at:  http://localhost:{port}/api         ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
    """)
    
    # Run the server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=config.DEBUG
    )
