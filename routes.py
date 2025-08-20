import os
import logging
from flask import render_template, request, jsonify, session, flash, redirect, url_for
from werkzeug.utils import secure_filename
import base64
from app import app
from civil_ai import CivilAI
from calculators import StructuralCalculator, MaterialEstimator, ProjectScheduler

# Initialize the AI assistant
civil_ai = CivilAI()
structural_calc = StructuralCalculator()
material_estimator = MaterialEstimator()
project_scheduler = ProjectScheduler()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page with introduction and features overview"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """AI Chat Assistant page"""
    # Initialize chat history in session if not exists
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('chat.html', chat_history=session['chat_history'])

@app.route('/chat', methods=['POST'])
def chat_post():
    """Handle AI chat queries"""
    try:
        user_message = request.form.get('message', '').strip()
        if not user_message:
            flash('Please enter a message', 'warning')
            return redirect(url_for('chat'))
        
        # Get AI response
        ai_response = civil_ai.get_civil_engineering_response(user_message)
        
        # Store in session
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'user': user_message,
            'ai': ai_response
        })
        
        # Keep only last 10 conversations
        if len(session['chat_history']) > 10:
            session['chat_history'] = session['chat_history'][-10:]
        
        session.modified = True
        
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        flash(f'Error getting AI response: {str(e)}', 'error')
    
    return redirect(url_for('chat'))

@app.route('/calculator')
def calculator():
    """Structural Calculator page"""
    return render_template('calculator.html')

@app.route('/calculator', methods=['POST'])
def calculator_post():
    """Handle structural calculations"""
    try:
        # Get form data
        span = float(request.form.get('span', 0))
        load = float(request.form.get('load', 0))
        concrete_grade = request.form.get('concrete_grade', 'M25')
        steel_grade = request.form.get('steel_grade', 'Fe415')
        
        if span <= 0 or load <= 0:
            flash('Please enter valid span and load values', 'warning')
            return redirect(url_for('calculator'))
        
        # Perform calculations
        results = structural_calc.calculate_beam_design(span, load, concrete_grade, steel_grade)
        
        return render_template('calculator.html', results=results, 
                             span=span, load=load, concrete_grade=concrete_grade, steel_grade=steel_grade)
        
    except ValueError:
        flash('Please enter valid numeric values', 'error')
    except Exception as e:
        logging.error(f"Calculator error: {str(e)}")
        flash(f'Calculation error: {str(e)}', 'error')
    
    return redirect(url_for('calculator'))

@app.route('/estimation')
def estimation():
    """Material Estimation (BOQ Generator) page"""
    return render_template('estimation.html')

@app.route('/estimation', methods=['POST'])
def estimation_post():
    """Handle material estimation calculations"""
    try:
        # Get room dimensions
        length = float(request.form.get('length', 0))
        width = float(request.form.get('width', 0))
        height = float(request.form.get('height', 0))
        
        # Get unit costs
        cement_rate = float(request.form.get('cement_rate', 450))  # ₹/bag
        sand_rate = float(request.form.get('sand_rate', 1500))     # ₹/m³
        aggregate_rate = float(request.form.get('aggregate_rate', 1200))  # ₹/m³
        steel_rate = float(request.form.get('steel_rate', 60))     # ₹/kg
        
        if length <= 0 or width <= 0 or height <= 0:
            flash('Please enter valid room dimensions', 'warning')
            return redirect(url_for('estimation'))
        
        # Calculate material quantities and costs
        estimation = material_estimator.calculate_quantities(
            length, width, height, cement_rate, sand_rate, aggregate_rate, steel_rate
        )
        
        return render_template('estimation.html', estimation=estimation,
                             length=length, width=width, height=height,
                             cement_rate=cement_rate, sand_rate=sand_rate,
                             aggregate_rate=aggregate_rate, steel_rate=steel_rate)
        
    except ValueError:
        flash('Please enter valid numeric values', 'error')
    except Exception as e:
        logging.error(f"Estimation error: {str(e)}")
        flash(f'Estimation error: {str(e)}', 'error')
    
    return redirect(url_for('estimation'))

@app.route('/scheduler')
def scheduler():
    """Project Scheduler page"""
    return render_template('scheduler.html')

@app.route('/scheduler', methods=['POST'])
def scheduler_post():
    """Handle project scheduling"""
    try:
        # Get task data from form
        tasks_data = []
        task_count = 0
        
        # Extract tasks from form data
        while f'task_{task_count}' in request.form:
            task_name = request.form.get(f'task_{task_count}', '').strip()
            duration = request.form.get(f'duration_{task_count}', '0')
            
            if task_name and duration:
                tasks_data.append({
                    'name': task_name,
                    'duration': int(duration)
                })
            task_count += 1
        
        if not tasks_data:
            flash('Please add at least one task', 'warning')
            return redirect(url_for('scheduler'))
        
        # Create schedule and get AI analysis
        schedule = project_scheduler.create_schedule(tasks_data)
        ai_analysis = civil_ai.analyze_project_schedule(tasks_data)
        
        return render_template('scheduler.html', schedule=schedule, 
                             ai_analysis=ai_analysis, tasks_data=tasks_data)
        
    except ValueError:
        flash('Please enter valid duration values', 'error')
    except Exception as e:
        logging.error(f"Scheduler error: {str(e)}")
        flash(f'Scheduling error: {str(e)}', 'error')
    
    return redirect(url_for('scheduler'))

@app.route('/safety')
def safety():
    """Site Safety & Image Analysis page"""
    return render_template('safety.html')

@app.route('/safety', methods=['POST'])
def safety_post():
    """Handle image upload and safety analysis"""
    try:
        if 'safety_image' not in request.files:
            flash('No image file selected', 'warning')
            return redirect(url_for('safety'))
        
        file = request.files['safety_image']
        
        if file.filename == '':
            flash('No image file selected', 'warning')
            return redirect(url_for('safety'))
        
        if file and allowed_file(file.filename):
            # Read and encode image
            image_data = file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Get AI analysis of the image for safety
            analysis = civil_ai.analyze_safety_image(base64_image)
            
            return render_template('safety.html', analysis=analysis)
        else:
            flash('Invalid file format. Please upload an image file (PNG, JPG, JPEG, GIF, BMP)', 'error')
            
    except Exception as e:
        logging.error(f"Safety analysis error: {str(e)}")
        flash(f'Image analysis error: {str(e)}', 'error')
    
    return redirect(url_for('safety'))

@app.route('/about')
def about():
    """About page with app information"""
    return render_template('about.html')

@app.route('/clear-chat')
def clear_chat():
    """Clear chat history"""
    session.pop('chat_history', None)
    flash('Chat history cleared', 'info')
    return redirect(url_for('chat'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500
