from app import create_app
from app.extensions.extensions import db
from flask import jsonify

app = create_app()

@app.route('/test-db')
def test_db():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'success',
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI'],
            'tables': db.engine.table_names()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'database_uri': app.config.get('SQLALCHEMY_DATABASE_URI')
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
