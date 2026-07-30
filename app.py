import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()  # Load .env file for local development
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, flash, g, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import joblib
from datetime import datetime, timedelta
import requests
from config import DB_DIR, MODEL_DIR, AUTH_DB, FEEDBACK_DB, TRUTH_DB, MODEL_FILE, VECTORIZER_FILE
from predict_bert import predict_news

from credibility_engine import compute_credibility
from source_verifier import verify_source



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# News API Configuration
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')  # Set via environment variable
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

# Load ML Model and Vectorizer
try:
    model = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
    print("Model and vectorizer loaded successfully!")
except FileNotFoundError:
    print("Model files not found. Please train and save the model first.")
    model = None
    vectorizer = None

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = get_db(AUTH_DB)
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return User(user['id'], user['username'])
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

# Database helper function
def get_db(db_name):
    os.makedirs(os.path.dirname(os.path.abspath(db_name)), exist_ok=True)
    db = sqlite3.connect(db_name, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA journal_mode=WAL;')
    except Exception:
        pass
    return db

# Initialize databases with enhanced error handling
def init_db():
    """Initialize all required databases with proper error handling"""
    try:
        print("Initializing databases...")
        
        # Auth database
        conn = sqlite3.connect(AUTH_DB)
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         username TEXT UNIQUE NOT NULL,
                         password_hash TEXT NOT NULL)''')
        conn.commit()
        conn.close()
        print("auth.db initialized")
        
        # TruthLens database for predictions
        conn = sqlite3.connect(TRUTH_DB)
        conn.execute('''CREATE TABLE IF NOT EXISTS predictions
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         user_id INTEGER NOT NULL,
                         headline TEXT NOT NULL,
                         prediction TEXT NOT NULL,
                         confidence REAL NOT NULL,
                         timestamp TEXT NOT NULL)''')
        conn.commit()
        conn.close()
        print("truthlens.db initialized")
        
        # Feedback database
        conn = sqlite3.connect(FEEDBACK_DB)
        conn.execute('''CREATE TABLE IF NOT EXISTS feedback
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         prediction_id INTEGER NOT NULL,
                         user_id INTEGER NOT NULL,
                         feedback TEXT NOT NULL,
                         timestamp TEXT NOT NULL)''')
        conn.commit()
        conn.close()
        print("feedback.db initialized")
        
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# Helper function for IST time
def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

# Initialize databases on startup
print("Starting TruthLens application...")
init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required!', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        try:
            conn = get_db(AUTH_DB)
            
            # Check if user already exists
            existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing_user:
                flash('Username already exists!', 'error')
                conn.close()
                return render_template('register.html')
            
            # Create new user
            password_hash = generate_password_hash(password)
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                        (username, password_hash))
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required!', 'error')
            return render_template('login.html')
        
        try:
            conn = get_db(AUTH_DB)
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                user_obj = User(user['id'], user['username'])
                login_user(user_obj)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password!', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Routes
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    print(f"Prediction request from user: {current_user.id}")

    headline = request.form.get('headline')
    if not headline:
        return jsonify({'error': 'No headline provided'}), 400

    headline = headline.strip()
    if len(headline) < 5:
        return jsonify({'error': 'Headline too short. Please enter a meaningful headline.'}), 400

    try:
        verdict, confidence = predict_news(headline)
        result = 'REAL' if verdict == 'REAL' or 'REAL' in str(verdict).upper() else 'FAKE'
        print(f"Prediction: {result}, Confidence: {confidence:.2f}%")

        # Save to DB
        try:
            conn = get_db(TRUTH_DB)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO predictions (user_id, headline, prediction, confidence, timestamp)
                              VALUES (?, ?, ?, ?, ?)''',
                           (current_user.id, headline, result, confidence, get_ist_time().isoformat()))
            prediction_id = cursor.lastrowid
            conn.commit()
            conn.close()

            print(f"✅ Prediction stored with ID: {prediction_id}")

            return jsonify({
                'result': result,
                'confidence': f"{confidence:.2f}%",
                'prediction_id': prediction_id
            })

        except Exception as db_error:
            print(f"❌ DB Error: {db_error}")
            return jsonify({'error': 'Database error occurred'}), 500

    except Exception as e:
        print(f"❌ BERT Prediction Error: {e}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    prediction_id = request.form.get('prediction_id')
    feedback = request.form.get('feedback')
    
    if not prediction_id or not feedback:
        return jsonify({'error': 'Missing data'}), 400
    
    if feedback not in ['accurate', 'wrong']:
        return jsonify({'error': 'Invalid feedback value'}), 400
    
    try:
        # Verify prediction exists and belongs to current user
        conn = get_db(TRUTH_DB)
        prediction = conn.execute('SELECT id FROM predictions WHERE id = ? AND user_id = ?',
                                (prediction_id, current_user.id)).fetchone()
        conn.close()
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Check if feedback already exists
        conn = get_db(FEEDBACK_DB)
        existing_feedback = conn.execute('SELECT id FROM feedback WHERE prediction_id = ? AND user_id = ?',
                                       (prediction_id, current_user.id)).fetchone()
        
        if existing_feedback:
            # Update existing feedback
            conn.execute('UPDATE feedback SET feedback = ?, timestamp = ? WHERE prediction_id = ? AND user_id = ?',
                        (feedback, get_ist_time().isoformat(), prediction_id, current_user.id))
        else:
            # Insert new feedback
            conn.execute('''INSERT INTO feedback (prediction_id, user_id, feedback, timestamp)
                            VALUES (?, ?, ?, ?)''',
                        (prediction_id, current_user.id, feedback, get_ist_time().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Feedback submitted: {feedback} for prediction {prediction_id}")
        
        return jsonify({'message': 'Feedback submitted successfully'})
        
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        return jsonify({'error': f'Failed to submit feedback: {str(e)}'}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Dashboard accessed by user: {current_user.id}")
    
    try:
        # Initialize default values
        total_predictions = 0
        accuracy_stats = {'accurate': 0, 'wrong': 0}
        accuracy_percentage = 0
        recent_feedback = []
        
        # Get total predictions
        try:
            conn = get_db(TRUTH_DB)
            result = conn.execute('SELECT COUNT(*) as count FROM predictions WHERE user_id = ?',
                                (current_user.id,)).fetchone()
            total_predictions = result['count'] if result else 0
            conn.close()
            print(f"Total predictions: {total_predictions}")
        except Exception as e:
            print(f"Error getting predictions: {e}")
        
        # Get feedback stats
        try:
            conn = get_db(FEEDBACK_DB)
            feedback_results = conn.execute('''SELECT feedback, COUNT(*) as count 
                                             FROM feedback WHERE user_id = ? 
                                             GROUP BY feedback''', (current_user.id,)).fetchall()
            conn.close()
            
            for result in feedback_results:
                if result['feedback'] in accuracy_stats:
                    accuracy_stats[result['feedback']] = result['count']
            
            total_feedback = accuracy_stats['accurate'] + accuracy_stats['wrong']
            accuracy_percentage = (accuracy_stats['accurate'] / total_feedback * 100) if total_feedback > 0 else 0
            
            print(f"Feedback stats: {accuracy_stats}")
        except Exception as e:
            print(f"Error getting feedback: {e}")
        
        # Get recent feedback with headlines
        try:
            conn_feedback = get_db(FEEDBACK_DB)
            conn_predictions = get_db(TRUTH_DB)            
            # Get recent feedback
            feedback_data = conn_feedback.execute('''SELECT prediction_id, feedback, timestamp 
                                                   FROM feedback WHERE user_id = ? 
                                                   ORDER BY timestamp DESC LIMIT 5''',
                                                (current_user.id,)).fetchall()
            
            recent_feedback = []
            for fb in feedback_data:
                # Get corresponding headline
                headline_data = conn_predictions.execute('SELECT headline FROM predictions WHERE id = ?',
                                                       (fb['prediction_id'],)).fetchone()
                recent_feedback.append({
                    'feedback': fb['feedback'],
                    'timestamp': fb['timestamp'],
                    'headline': headline_data['headline'] if headline_data else 'Headline not found'
                })
            
            conn_feedback.close()
            conn_predictions.close()
            
            print(f"Recent feedback count: {len(recent_feedback)}")
        except Exception as e:
            print(f"Error getting recent feedback: {e}")
        
        return render_template('dashboard.html', 
                             total_predictions=total_predictions,
                             accuracy_percentage=accuracy_percentage,
                             recent_feedback=recent_feedback,
                             accuracy_stats=accuracy_stats)
                             
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash(f'Dashboard error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/history')
@login_required
def history():
    print(f"History accessed by user: {current_user.id}")
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '').strip()
    filter_type = request.args.get('filter_type', 'all')
    sort_by = request.args.get('sort_by', 'newest')
    
    try:
        conn = get_db(TRUTH_DB)
        
        # Build base query
        base_query = 'SELECT * FROM predictions WHERE user_id = ?'
        query_params = [current_user.id]
        
        # Apply search filter
        if search_query:
            base_query += ' AND headline LIKE ?'
            query_params.append(f'%{search_query}%')
        
        # Apply result filter
        if filter_type == 'real':
            base_query += ' AND prediction = ?'
            query_params.append('REAL')
        elif filter_type == 'fake':
            base_query += ' AND prediction = ?'
            query_params.append('FAKE')
        
        # Apply sorting
        if sort_by == 'newest':
            base_query += ' ORDER BY timestamp DESC'
        elif sort_by == 'oldest':
            base_query += ' ORDER BY timestamp ASC'
        elif sort_by == 'confidence_high':
            base_query += ' ORDER BY confidence DESC'
        elif sort_by == 'confidence_low':
            base_query += ' ORDER BY confidence ASC'
        else:
            base_query += ' ORDER BY timestamp DESC'
        
        # Get all matching results
        all_predictions = conn.execute(base_query, query_params).fetchall()
        total_count = len(all_predictions)
        
        # Calculate pagination
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        page = max(1, min(page, total_pages))  # Ensure valid page number
        
        # Get paginated results
        offset = (page - 1) * per_page
        paginated_query = base_query + f' LIMIT ? OFFSET ?'
        predictions_list = conn.execute(paginated_query, 
                                       query_params + [per_page, offset]).fetchall()
        
        # Get stats
        total_predictions = conn.execute(
            'SELECT COUNT(*) as count FROM predictions WHERE user_id = ?',
            (current_user.id,)
        ).fetchone()['count']
        
        real_count = conn.execute(
            'SELECT COUNT(*) as count FROM predictions WHERE user_id = ? AND prediction = ?',
            (current_user.id, 'REAL')
        ).fetchone()['count']
        
        fake_count = conn.execute(
            'SELECT COUNT(*) as count FROM predictions WHERE user_id = ? AND prediction = ?',
            (current_user.id, 'FAKE')
        ).fetchone()['count']
        
        conn.close()
        
        # Convert to list of dictionaries with datetime objects
        predictions_data = []
        for row in predictions_list:
            pred_dict = dict(row)
            # Convert string timestamp to datetime object
            try:
                pred_dict['timestamp'] = datetime.fromisoformat(pred_dict['timestamp'])
            except:
                pred_dict['timestamp'] = datetime.now()
            predictions_data.append(pred_dict)
        
        # Create pagination object
        class PaginationHelper:
            def __init__(self, items, page, per_page, total):
                self.items = items
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = (total + per_page - 1) // per_page if total > 0 else 1
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None
            
            def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
                """Generate page numbers for pagination"""
                last = 0
                for num in range(1, self.pages + 1):
                    if (num <= left_edge or
                        (num > self.page - left_current - 1 and num < self.page + right_current) or
                        num > self.pages - right_edge):
                        if last + 1 != num:
                            yield None
                        yield num
                        last = num
        
        predictions = PaginationHelper(
            items=predictions_data,
            page=page,
            per_page=per_page,
            total=total_count
        )
        
        print(f"History: Page {page}/{predictions.pages}, Total: {total_count}")
        print(f"Stats: Total={total_predictions}, Real={real_count}, Fake={fake_count}")
        
        return render_template('history.html',
                             predictions=predictions,
                             total_predictions=total_predictions,
                             real_count=real_count,
                             fake_count=fake_count,
                             search_query=search_query,
                             filter_type=filter_type,
                             sort_by=sort_by,
                             per_page=per_page)
        
    except Exception as e:
        print(f"❌ History error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return empty pagination on error
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
            per_page = per_page
            
            def iter_pages(self, **kwargs):
                return []
        
        flash(f'Error loading history: {str(e)}', 'error')
        return render_template('history.html',
                             predictions=EmptyPagination(),
                             total_predictions=0,
                             real_count=0,
                             fake_count=0,
                             search_query=search_query,
                             filter_type=filter_type,
                             sort_by=sort_by,
                             per_page=per_page)


@app.route('/api/prediction/<int:prediction_id>')
@login_required
def get_prediction_details(prediction_id):
    """Get detailed information about a prediction"""
    try:
        conn = get_db(TRUTH_DB)
        prediction = conn.execute(
            'SELECT * FROM predictions WHERE id = ? AND user_id = ?',
            (prediction_id, current_user.id)
        ).fetchone()
        conn.close()
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        pred_dict = dict(prediction)
        
        return jsonify({
            'id': pred_dict['id'],
            'headline': pred_dict['headline'],
            'prediction': pred_dict['prediction'],
            'confidence': pred_dict['confidence'],
            'timestamp': pred_dict['timestamp'],
            'source': 'User Input'
        })
        
    except Exception as e:
        print(f"Error getting prediction details: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/prediction/<int:prediction_id>/delete', methods=['POST'])
@login_required
def delete_prediction(prediction_id):
    """Delete a prediction"""
    try:
        conn = get_db(TRUTH_DB)
        
        # Check if prediction exists and belongs to current user
        prediction = conn.execute(
            'SELECT id FROM predictions WHERE id = ? AND user_id = ?',
            (prediction_id, current_user.id)
        ).fetchone()
        
        if not prediction:
            conn.close()
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Delete the prediction
        conn.execute('DELETE FROM predictions WHERE id = ?', (prediction_id,))
        conn.commit()
        conn.close()
        
        # Also delete associated feedback
        try:
            feedback_conn = get_db(FEEDBACK_DB)
            feedback_conn.execute('DELETE FROM feedback WHERE prediction_id = ?', (prediction_id,))
            feedback_conn.commit()
            feedback_conn.close()
        except Exception as fb_error:
            print(f"Warning: Could not delete feedback: {fb_error}")
        
        print(f"✅ Deleted prediction {prediction_id}")
        return jsonify({'success': True, 'message': 'Prediction deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/export/history')
@login_required
def export_history():
    """Export history as CSV"""
    return export_csv()  # Reuse existing export_csv function



# ===== LEGAL PAGES ROUTES =====
@app.route('/privacy')
def privacy():
    """Privacy Policy Page"""
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    """Terms of Service Page"""
    return render_template('terms.html')


@app.route('/cookies')
def cookies():
    """Cookie Policy Page"""
    return render_template('cookies.html')






@app.route('/live-news')
@login_required
def live_news():
    if not NEWS_API_KEY or NEWS_API_KEY == 'your-news-api-key':
        flash('News API key not configured. Please contact administrator.', 'error')
        return render_template('live_news.html', articles=[])
    
    try:
        params = {
            'apiKey': NEWS_API_KEY,
            'language': 'en',
            'country': 'us',
            'pageSize': 20,
            'sortBy': 'publishedAt'
        }
        
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        news_data = response.json()
        
        if response.status_code == 200:
            articles = news_data.get('articles', [])
            
            # Filter and clean articles
            cleaned_articles = []
            for article in articles:
                # Skip articles with missing or removed titles
                if not article.get('title') or article['title'] in ['[Removed]', '', None]:
                    continue
                
                # Clean up the article data
                cleaned_article = {
                    'title': article.get('title', '').strip(),
                    'description': article.get('description', '').strip() if article.get('description') else None,
                    'url': article.get('url', '#'),
                    'urlToImage': article.get('urlToImage'),
                    'publishedAt': article.get('publishedAt'),
                    'source': {
                        'name': article.get('source', {}).get('name', 'Unknown Source')
                    }
                }
                
                # Only add articles with valid titles
                if len(cleaned_article['title']) > 5:
                    cleaned_articles.append(cleaned_article)
            
            print(f"Fetched {len(cleaned_articles)} valid articles")
            return render_template('live_news.html', articles=cleaned_articles)
        else:
            error_msg = news_data.get('message', 'Unknown error')
            flash(f'Error fetching news: {error_msg}', 'error')
            return render_template('live_news.html', articles=[])
    
    except requests.RequestException as e:
        print(f"News API request error: {e}")
        flash('Unable to fetch live news. Please try again later.', 'error')
        return render_template('live_news.html', articles=[])
    except Exception as e:
        print(f"Live news error: {e}")
        flash(f'Error fetching news: {str(e)}', 'error')
        return render_template('live_news.html', articles=[])


@app.route('/export-csv')
@login_required
def export_csv():
    try:
        conn = get_db(TRUTH_DB)
        predictions = conn.execute('''SELECT headline, prediction, confidence, timestamp 
                                     FROM predictions WHERE user_id = ? 
                                     ORDER BY timestamp DESC''',
                                  (current_user.id,)).fetchall()
        conn.close()
        
        if not predictions:
            flash('No prediction data to export.', 'info')
            return redirect(url_for('dashboard'))
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Headline', 'Prediction', 'Confidence (%)', 'Timestamp (IST)'])
        
        for prediction in predictions:
            writer.writerow([
                prediction['headline'], 
                prediction['prediction'], 
                f"{prediction['confidence']:.2f}",
                prediction['timestamp']
            ])
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=truthlens_predictions_{current_user.username}_{datetime.now().strftime("%Y%m%d")}.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
        
    except Exception as e:
        print(f"Export error: {e}")
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

    # Debug route (remove in production)
    @app.route('/debug-data')
    @login_required
    def debug_data():
        debug_info = {
            'user_id': current_user.id,
            'username': current_user.username
        }
    
    # Check predictions
    try:
        conn = get_db(TRUTH_DB)
        predictions = conn.execute('SELECT * FROM predictions WHERE user_id = ?', (current_user.id,)).fetchall()
        debug_info['predictions'] = [dict(row) for row in predictions]
        debug_info['predictions_count'] = len(predictions)
        conn.close()
    except Exception as e:
        debug_info['predictions_error'] = str(e)
    
    # Check feedback
    try:
        conn = get_db(FEEDBACK_DB)
        feedback = conn.execute('SELECT * FROM feedback WHERE user_id = ?', (current_user.id,)).fetchall()
        debug_info['feedback'] = [dict(row) for row in feedback]
        debug_info['feedback_count'] = len(feedback)
        conn.close()
    except Exception as e:
        debug_info['feedback_error'] = str(e)
    
    return jsonify(debug_info)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        flash('Page not found.', 'error')
        return redirect(url_for('index'))

    @app.errorhandler(500)
    def internal_error(error):
        flash('An internal error occurred. Please try again.', 'error')
        return redirect(url_for('index'))



# ===== SETTINGS & HELP ROUTES =====

@app.route('/settings')
@login_required
def settings():
    """User Settings Page"""
    try:
        # Get user statistics for display
        conn = get_db(TRUTH_DB)
        total_predictions = conn.execute(
            'SELECT COUNT(*) as count FROM predictions WHERE user_id = ?',
            (current_user.id,)
        ).fetchone()['count']
        conn.close()
        
        return render_template('settings.html', 
                             total_predictions=total_predictions)
    except Exception as e:
        print(f"Settings page error: {e}")
        return render_template('settings.html', 
                             total_predictions=0)


@app.route('/help')
def help():
    """Help & Support Page"""
    return render_template('help.html')


# ===== API ENDPOINTS FOR SETTINGS =====

@app.route('/api/settings/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        data = request.get_json()
        
        # In production, update database with new profile info
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/settings/update-password', methods=['POST'])
@login_required
def update_password():
    """Update user password"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Verify current password
        conn = get_db(AUTH_DB)
        user = conn.execute('SELECT * FROM users WHERE id = ?', 
                           (current_user.id,)).fetchone()
        conn.close()
        
        if not user or not check_password_hash(user['password_hash'], current_password):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401
        
        # Update password
        new_password_hash = generate_password_hash(new_password)
        conn = get_db(AUTH_DB)
        conn.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                    (new_password_hash, current_user.id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Password updated successfully'
        })
        
    except Exception as e:
        print(f"Password update error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update password'
        }), 500


@app.route('/api/help/contact', methods=['POST'])
def submit_contact_form():
    """Submit help contact form"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        # In production, send email or store in database
        print(f"Contact form submission:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        
        # Here you would typically:
        # 1. Send email to support team
        # 2. Store in database for tracking
        # 3. Send confirmation email to user
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully'
        })
        
    except Exception as e:
        print(f"Contact form error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to send message'
        }), 500




# ===== CREDIBILITY & SOURCE VERIFICATION API ROUTES =====

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    """Full credibility analysis – BERT + linguistic + source (requires login)"""
    data = request.get_json(force=True) or {}
    headline = (data.get('headline') or '').strip()
    source_url = (data.get('source_url') or '').strip() or None

    if not headline or len(headline) < 5:
        return jsonify({'error': 'Please provide a valid headline (min 5 chars).'}), 400

    try:
        verdict, confidence = predict_news(headline)
        prediction = 'REAL' if verdict == 'REAL' or 'REAL' in str(verdict).upper() else 'FAKE'

        # Extract domain from source URL if provided
        domain = None
        if source_url:
            from source_verifier import extract_domain
            domain = extract_domain(source_url)

        # Multi-factor credibility score
        cred = compute_credibility(headline, confidence, prediction, domain)

        # Persist to DB
        conn = get_db(TRUTH_DB)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO predictions (user_id, headline, prediction, confidence, timestamp) VALUES (?, ?, ?, ?, ?)',
            (current_user.id, headline, prediction, confidence, get_ist_time().isoformat())
        )
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'prediction_id': prediction_id,
            'verdict': prediction,
            'bert_confidence': round(confidence, 2),
            **cred,
        })

    except Exception as e:
        print(f'❌ Analyze error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/credibility-score', methods=['POST', 'OPTIONS'])
def credibility_score_public():
    """Public credibility score API (no auth) – used by browser extension."""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json(force=True) or {}
    headline = (data.get('headline') or '').strip()
    source_url = (data.get('source_url') or '').strip() or None

    if not headline or len(headline) < 5:
        return jsonify({'error': 'Headline too short'}), 400

    try:
        verdict, confidence = predict_news(headline)
        prediction = 'REAL' if verdict == 'REAL' or 'REAL' in str(verdict).upper() else 'FAKE'

        domain = None
        if source_url:
            from source_verifier import extract_domain
            domain = extract_domain(source_url)

        cred = compute_credibility(headline, confidence, prediction, domain)
        return jsonify({'verdict': prediction, 'bert_confidence': round(confidence, 2), **cred})

    except Exception as e:
        print(f'❌ Public credibility score error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/verify-source', methods=['POST', 'OPTIONS'])
def api_verify_source():
    """Source verification endpoint – checks domain trust level."""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json(force=True) or {}
    url = (data.get('url') or data.get('domain') or '').strip()

    if not url:
        return jsonify({'error': 'Please provide a url or domain field.'}), 400

    try:
        result = verify_source(url)
        return jsonify(result)
    except Exception as e:
        print(f'❌ Source verify error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/source-check')
def source_check():
    """Source credibility check page"""
    return render_template('source_check.html')


@app.route('/install-extension')
def install_extension():
    """Browser extension installation guide page"""
    return render_template('install_extension.html')


@app.route('/download-extension')
def download_extension():
    """Zip and serve the browser_extension folder for download."""
    import zipfile
    import io as _io
    ext_dir = os.path.join(BASE_DIR, 'browser_extension')
    if not os.path.isdir(ext_dir):
        flash('Extension package not found.', 'error')
        return redirect(url_for('install_extension'))

    buf = _io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ext_dir):
            # Skip __pycache__ and hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                abs_path = os.path.join(root, file)
                arc_name = os.path.relpath(abs_path, os.path.dirname(ext_dir))
                zf.write(abs_path, arc_name)
    buf.seek(0)

    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = 'attachment; filename=factora-extension.zip'
    return response


# Error handlers
@app.errorhandler(404)
def not_found(error):
    flash('Page not found.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("FacTora application ready!")
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    print(f"Visit: http://localhost:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
