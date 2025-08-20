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

# AJAX endpoints for dynamic chat
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """AJAX endpoint for chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Please enter a message'}), 400
        
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
        
        return jsonify({
            'success': True,
            'ai_response': ai_response,
            'user_message': user_message
        })
        
    except Exception as e:
        logging.error(f"AJAX Chat error: {str(e)}")
        return jsonify({'error': f'Error getting AI response: {str(e)}'}), 500

# Unit conversion helper functions
def meters_to_feet(meters):
    """Convert meters to feet"""
    return meters * 3.28084

def feet_to_meters(feet):
    """Convert feet to meters"""
    return feet / 3.28084

def kg_to_lbs(kg):
    """Convert kg to pounds"""
    return kg * 2.20462

# Concrete Mix Calculator routes
@app.route('/concrete-calculator')
def concrete_calculator():
    """Concrete Mix Calculator page"""
    return render_template('concrete_calculator.html')

@app.route('/api/concrete-mix', methods=['POST'])
def api_concrete_mix():
    """AJAX endpoint for concrete mix calculations"""
    try:
        data = request.get_json()
        
        # Get inputs
        grade = data.get('grade', 'M20')
        volume = float(data.get('volume', 0))  # in cubic meters
        water_cement_ratio = float(data.get('water_cement_ratio', 0.5))
        unit = data.get('unit', 'meters')  # meters or feet
        
        # Convert to meters if input is in feet
        if unit == 'feet':
            volume = feet_to_meters(volume) ** 3  # cubic feet to cubic meters
        
        if volume <= 0:
            return jsonify({'error': 'Please enter valid volume'}), 400
        
        # Concrete mix ratios for different grades (cement:sand:aggregate)
        mix_ratios = {
            'M15': {'cement': 1, 'sand': 2, 'aggregate': 4},
            'M20': {'cement': 1, 'sand': 1.5, 'aggregate': 3},
            'M25': {'cement': 1, 'sand': 1, 'aggregate': 2},
            'M30': {'cement': 1, 'sand': 1, 'aggregate': 1.5},
            'M35': {'cement': 1, 'sand': 1, 'aggregate': 1.2}
        }
        
        if grade not in mix_ratios:
            return jsonify({'error': 'Invalid concrete grade'}), 400
        
        ratio = mix_ratios[grade]
        total_ratio = ratio['cement'] + ratio['sand'] + ratio['aggregate']
        
        # Calculate quantities
        cement_volume = (ratio['cement'] / total_ratio) * volume
        sand_volume = (ratio['sand'] / total_ratio) * volume
        aggregate_volume = (ratio['aggregate'] / total_ratio) * volume
        
        # Convert to weight (approximate densities in kg/m³)
        cement_weight = cement_volume * 1440  # kg
        sand_weight = sand_volume * 1600  # kg
        aggregate_weight = aggregate_volume * 1500  # kg
        
        # Convert to bags (1 bag = 50kg)
        cement_bags = cement_weight / 50
        water_required = cement_weight * water_cement_ratio  # liters
        
        results = {
            'grade': grade,
            'volume': volume,
            'cement': {
                'weight_kg': round(cement_weight, 2),
                'bags': round(cement_bags, 2),
                'volume_m3': round(cement_volume, 3)
            },
            'sand': {
                'weight_kg': round(sand_weight, 2),
                'volume_m3': round(sand_volume, 3)
            },
            'aggregate': {
                'weight_kg': round(aggregate_weight, 2),
                'volume_m3': round(aggregate_volume, 3)
            },
            'water_liters': round(water_required, 2),
            'mix_ratio': f"{ratio['cement']}:{ratio['sand']}:{ratio['aggregate']}"
        }
        
        # Add feet conversions if requested
        if unit == 'feet':
            results['cement']['volume_ft3'] = round(cement_volume * 35.3147, 3)
            results['sand']['volume_ft3'] = round(sand_volume * 35.3147, 3)
            results['aggregate']['volume_ft3'] = round(aggregate_volume * 35.3147, 3)
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logging.error(f"Concrete mix calculation error: {str(e)}")
        return jsonify({'error': f'Calculation error: {str(e)}'}), 500

# Steel Weight Calculator routes
@app.route('/steel-calculator')
def steel_calculator():
    """Steel Weight Calculator page"""
    return render_template('steel_calculator.html')

@app.route('/api/steel-weight', methods=['POST'])
def api_steel_weight():
    """AJAX endpoint for steel weight calculations"""
    try:
        data = request.get_json()
        bars = data.get('bars', [])
        unit = data.get('unit', 'meters')  # meters or feet
        
        if not bars:
            return jsonify({'error': 'Please add at least one steel bar'}), 400
        
        total_weight = 0
        bar_results = []
        
        for bar in bars:
            diameter = float(bar.get('diameter', 0))  # mm
            length = float(bar.get('length', 0))  # meters or feet
            quantity = int(bar.get('quantity', 1))
            
            if diameter <= 0 or length <= 0 or quantity <= 0:
                continue
            
            # Convert length to meters if in feet
            if unit == 'feet':
                length_m = feet_to_meters(length)
            else:
                length_m = length
            
            # Weight formula: Weight (kg) = (D²/162) × L × Quantity
            # Where D = diameter in mm, L = length in meters
            weight_per_bar = (diameter * diameter / 162) * length_m
            total_bar_weight = weight_per_bar * quantity
            total_weight += total_bar_weight
            
            bar_result = {
                'diameter': diameter,
                'length': length,
                'quantity': quantity,
                'weight_per_bar_kg': round(weight_per_bar, 3),
                'total_weight_kg': round(total_bar_weight, 3),
                'unit': unit
            }
            
            # Add imperial units if needed
            if unit == 'feet':
                bar_result['weight_per_bar_lbs'] = round(kg_to_lbs(weight_per_bar), 3)
                bar_result['total_weight_lbs'] = round(kg_to_lbs(total_bar_weight), 3)
            
            bar_results.append(bar_result)
        
        results = {
            'bars': bar_results,
            'total_weight_kg': round(total_weight, 2),
            'total_bars': sum(bar['quantity'] for bar in bars if bar.get('diameter', 0) > 0)
        }
        
        if unit == 'feet':
            results['total_weight_lbs'] = round(kg_to_lbs(total_weight), 2)
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logging.error(f"Steel weight calculation error: {str(e)}")
        return jsonify({'error': f'Calculation error: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500
