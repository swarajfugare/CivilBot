import os
import logging
from flask import render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import base64
from app import app, db
from civil_ai import CivilAI
from calculators import StructuralCalculator, MaterialEstimator, ProjectScheduler
from models import User, ChatHistory
from forms import LoginForm, RegistrationForm, UnitConverterForm, MaterialEstimatorForm

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

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Home page with introduction and features overview"""
    return render_template('index.html')

@app.route('/chat')
@login_required
def chat():
    """AI Chat Assistant page"""
    # Get chat history from database for current user
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at).limit(20).all()
    return render_template('chat.html', chat_history=chat_history)

# AJAX endpoints for dynamic chat
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """AJAX endpoint for chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Please enter a message'}), 400
        
        # Get AI response
        ai_response = civil_ai.get_civil_engineering_response(user_message)
        
        # Store in database
        chat_record = ChatHistory(
            user_id=current_user.id,
            user_message=user_message,
            bot_response=ai_response
        )
        db.session.add(chat_record)
        db.session.commit()
        
        # Keep only last 50 conversations per user
        total_chats = ChatHistory.query.filter_by(user_id=current_user.id).count()
        if total_chats > 50:
            old_chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at).limit(total_chats - 50).all()
            for chat in old_chats:
                db.session.delete(chat)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'ai_response': ai_response,
            'user_message': user_message
        })
        
    except Exception as e:
        logging.error(f"AJAX Chat error: {str(e)}")
        return jsonify({'error': f'Error getting AI response: {str(e)}'}), 500

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
@login_required
def clear_chat():
    """Clear chat history for current user"""
    ChatHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Chat history cleared', 'info')
    return redirect(url_for('chat'))

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
@login_required
def steel_calculator():
    """Steel Weight Calculator page"""
    return render_template('steel_calculator.html')

# Unit Converter routes
@app.route('/unit-converter', methods=['GET', 'POST'])
@login_required
def unit_converter():
    """Unit Converter Tool"""
    form = UnitConverterForm()
    result = None
    
    # Dynamic unit choices based on conversion type
    if request.method == 'POST' and form.conversion_type.data:
        conversion_type = form.conversion_type.data
        
        if conversion_type == 'length':
            form.from_unit.choices = [('m', 'Meters'), ('ft', 'Feet'), ('mm', 'Millimeters'), ('cm', 'Centimeters'), ('km', 'Kilometers')]
            form.to_unit.choices = [('m', 'Meters'), ('ft', 'Feet'), ('mm', 'Millimeters'), ('cm', 'Centimeters'), ('km', 'Kilometers')]
        elif conversion_type == 'weight':
            form.from_unit.choices = [('kg', 'Kilograms'), ('ton', 'Tons'), ('g', 'Grams'), ('lb', 'Pounds')]
            form.to_unit.choices = [('kg', 'Kilograms'), ('ton', 'Tons'), ('g', 'Grams'), ('lb', 'Pounds')]
        elif conversion_type == 'area':
            form.from_unit.choices = [('sqm', 'Square Meters'), ('sqft', 'Square Feet'), ('acre', 'Acres'), ('hectare', 'Hectares')]
            form.to_unit.choices = [('sqm', 'Square Meters'), ('sqft', 'Square Feet'), ('acre', 'Acres'), ('hectare', 'Hectares')]
        elif conversion_type == 'volume':
            form.from_unit.choices = [('cum', 'Cubic Meters'), ('cuft', 'Cubic Feet'), ('liter', 'Liters')]
            form.to_unit.choices = [('cum', 'Cubic Meters'), ('cuft', 'Cubic Feet'), ('liter', 'Liters')]
        elif conversion_type == 'pressure':
            form.from_unit.choices = [('nmm2', 'N/mm²'), ('psi', 'PSI'), ('mpa', 'MPa'), ('bar', 'Bar')]
            form.to_unit.choices = [('nmm2', 'N/mm²'), ('psi', 'PSI'), ('mpa', 'MPa'), ('bar', 'Bar')]
        
        if form.validate_on_submit():
            result = convert_units(form.value.data, form.from_unit.data, form.to_unit.data, conversion_type)
    
    return render_template('unit_converter.html', form=form, result=result)

# Material Estimator routes
@app.route('/material-estimator', methods=['GET', 'POST'])
@login_required
def material_estimator_route():
    """Material Estimator Tool"""
    form = MaterialEstimatorForm()
    result = None
    
    if form.validate_on_submit():
        area = form.area.data
        construction_type = form.construction_type.data
        result = estimate_materials(area, construction_type)
    
    return render_template('material_estimator.html', form=form, result=result)

def convert_units(value, from_unit, to_unit, conversion_type):
    """Convert units based on type and return result"""
    try:
        # Length conversions
        if conversion_type == 'length':
            # Convert to meters first
            if from_unit == 'ft':
                value_in_m = value / 3.28084
            elif from_unit == 'mm':
                value_in_m = value / 1000
            elif from_unit == 'cm':
                value_in_m = value / 100
            elif from_unit == 'km':
                value_in_m = value * 1000
            else:  # meters
                value_in_m = value
                
            # Convert from meters to target unit
            if to_unit == 'ft':
                result_value = value_in_m * 3.28084
            elif to_unit == 'mm':
                result_value = value_in_m * 1000
            elif to_unit == 'cm':
                result_value = value_in_m * 100
            elif to_unit == 'km':
                result_value = value_in_m / 1000
            else:  # meters
                result_value = value_in_m
                
        # Weight conversions
        elif conversion_type == 'weight':
            # Convert to kg first
            if from_unit == 'ton':
                value_in_kg = value * 1000
            elif from_unit == 'g':
                value_in_kg = value / 1000
            elif from_unit == 'lb':
                value_in_kg = value / 2.20462
            else:  # kg
                value_in_kg = value
                
            # Convert from kg to target unit
            if to_unit == 'ton':
                result_value = value_in_kg / 1000
            elif to_unit == 'g':
                result_value = value_in_kg * 1000
            elif to_unit == 'lb':
                result_value = value_in_kg * 2.20462
            else:  # kg
                result_value = value_in_kg
                
        # Area conversions
        elif conversion_type == 'area':
            # Convert to sqm first
            if from_unit == 'sqft':
                value_in_sqm = value / 10.7639
            elif from_unit == 'acre':
                value_in_sqm = value * 4047
            elif from_unit == 'hectare':
                value_in_sqm = value * 10000
            else:  # sqm
                value_in_sqm = value
                
            # Convert from sqm to target unit
            if to_unit == 'sqft':
                result_value = value_in_sqm * 10.7639
            elif to_unit == 'acre':
                result_value = value_in_sqm / 4047
            elif to_unit == 'hectare':
                result_value = value_in_sqm / 10000
            else:  # sqm
                result_value = value_in_sqm
                
        # Volume conversions
        elif conversion_type == 'volume':
            # Convert to cum first
            if from_unit == 'cuft':
                value_in_cum = value / 35.3147
            elif from_unit == 'liter':
                value_in_cum = value / 1000
            else:  # cum
                value_in_cum = value
                
            # Convert from cum to target unit
            if to_unit == 'cuft':
                result_value = value_in_cum * 35.3147
            elif to_unit == 'liter':
                result_value = value_in_cum * 1000
            else:  # cum
                result_value = value_in_cum
                
        # Pressure conversions
        elif conversion_type == 'pressure':
            # Convert to N/mm² first
            if from_unit == 'psi':
                value_in_nmm2 = value / 145.038
            elif from_unit == 'mpa':
                value_in_nmm2 = value
            elif from_unit == 'bar':
                value_in_nmm2 = value / 10
            else:  # nmm2
                value_in_nmm2 = value
                
            # Convert from N/mm² to target unit
            if to_unit == 'psi':
                result_value = value_in_nmm2 * 145.038
            elif to_unit == 'mpa':
                result_value = value_in_nmm2
            elif to_unit == 'bar':
                result_value = value_in_nmm2 * 10
            else:  # nmm2
                result_value = value_in_nmm2
        
        return {
            'original_value': value,
            'from_unit': from_unit,
            'result_value': round(result_value, 6),
            'to_unit': to_unit,
            'conversion_type': conversion_type
        }
        
    except Exception as e:
        logging.error(f"Unit conversion error: {str(e)}")
        return {'error': str(e)}

def estimate_materials(area, construction_type):
    """Estimate materials based on area and construction type"""
    try:
        if construction_type == 'brick_wall':
            # For 9-inch brick wall
            bricks = area * 120  # bricks per sqm
            cement_bags = area * 0.3  # bags per sqm
            sand_cum = area * 0.05  # cubic meters per sqm
            
            return {
                'construction_type': 'Brick Wall (9 inch)',
                'area': area,
                'materials': {
                    'Bricks': f"{int(bricks)} nos",
                    'Cement': f"{cement_bags:.2f} bags (50kg each)",
                    'Sand': f"{sand_cum:.3f} cubic meters",
                    'Water': f"{cement_bags * 25:.0f} liters"
                }
            }
            
        elif construction_type == 'concrete_slab':
            # For 6-inch RCC slab
            concrete_cum = area * 0.152  # cubic meters
            cement_bags = concrete_cum * 7  # bags per cum
            sand_cum = concrete_cum * 0.42  # cubic meters
            aggregate_cum = concrete_cum * 0.84  # cubic meters
            steel_kg = area * 12  # kg per sqm
            
            return {
                'construction_type': 'RCC Slab (6 inch)',
                'area': area,
                'materials': {
                    'Concrete Volume': f"{concrete_cum:.3f} cubic meters",
                    'Cement': f"{cement_bags:.2f} bags (50kg each)",
                    'Sand': f"{sand_cum:.3f} cubic meters",
                    'Aggregate (20mm)': f"{aggregate_cum:.3f} cubic meters",
                    'Steel Reinforcement': f"{steel_kg:.2f} kg",
                    'Water': f"{cement_bags * 25:.0f} liters"
                }
            }
            
        elif construction_type == 'plaster':
            # For 12mm thick plaster
            cement_bags = area * 0.18  # bags per sqm
            sand_cum = area * 0.015  # cubic meters per sqm
            
            return {
                'construction_type': 'Plastering (12mm thick)',
                'area': area,
                'materials': {
                    'Cement': f"{cement_bags:.2f} bags (50kg each)",
                    'Sand': f"{sand_cum:.3f} cubic meters",
                    'Water': f"{cement_bags * 25:.0f} liters"
                }
            }
            
        elif construction_type == 'flooring':
            # For tile flooring
            tiles_sqm = area * 1.05  # 5% extra for wastage
            cement_bags = area * 0.25  # bags per sqm
            sand_cum = area * 0.02  # cubic meters per sqm
            
            return {
                'construction_type': 'Tile Flooring',
                'area': area,
                'materials': {
                    'Tiles': f"{tiles_sqm:.2f} square meters (with 5% wastage)",
                    'Cement': f"{cement_bags:.2f} bags (50kg each)",
                    'Sand': f"{sand_cum:.3f} cubic meters",
                    'Tile Adhesive': f"{area * 5:.2f} kg",
                    'Water': f"{cement_bags * 25:.0f} liters"
                }
            }
            
        elif construction_type == 'foundation':
            # For strip foundation (1m deep, 0.5m wide)
            length = area  # assuming area represents length for strip foundation
            concrete_cum = length * 1 * 0.5  # cubic meters
            cement_bags = concrete_cum * 6.5  # bags per cum
            sand_cum = concrete_cum * 0.45  # cubic meters
            aggregate_cum = concrete_cum * 0.9  # cubic meters
            steel_kg = concrete_cum * 60  # kg per cum
            
            return {
                'construction_type': 'Strip Foundation (1m deep, 0.5m wide)',
                'length': area,
                'materials': {
                    'Concrete Volume': f"{concrete_cum:.3f} cubic meters",
                    'Cement': f"{cement_bags:.2f} bags (50kg each)",
                    'Sand': f"{sand_cum:.3f} cubic meters",
                    'Aggregate (20mm)': f"{aggregate_cum:.3f} cubic meters",
                    'Steel Reinforcement': f"{steel_kg:.2f} kg",
                    'Water': f"{cement_bags * 25:.0f} liters",
                    'Excavation Volume': f"{concrete_cum:.3f} cubic meters"
                }
            }
        
    except Exception as e:
        logging.error(f"Material estimation error: {str(e)}")
        return {'error': str(e)}

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
