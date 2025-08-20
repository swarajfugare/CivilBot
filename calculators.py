import math
import logging
from datetime import datetime, timedelta

class StructuralCalculator:
    """Calculator for structural design calculations"""
    
    def __init__(self):
        # Material properties
        self.concrete_grades = {
            'M15': {'fck': 15, 'density': 2400},
            'M20': {'fck': 20, 'density': 2400},
            'M25': {'fck': 25, 'density': 2500},
            'M30': {'fck': 30, 'density': 2500},
            'M35': {'fck': 35, 'density': 2500}
        }
        
        self.steel_grades = {
            'Fe415': {'fy': 415, 'density': 7850},
            'Fe500': {'fy': 500, 'density': 7850},
            'Fe550': {'fy': 550, 'density': 7850}
        }
    
    def calculate_beam_design(self, span, load, concrete_grade, steel_grade):
        """Calculate beam dimensions and reinforcement"""
        try:
            # Get material properties
            fck = self.concrete_grades[concrete_grade]['fck']  # N/mm²
            fy = self.steel_grades[steel_grade]['fy']  # N/mm²
            
            # Convert span from meters to mm
            span_mm = span * 1000
            
            # Calculate maximum bending moment (kN-m for simply supported beam with UDL)
            moment = (load * span**2) / 8  # kN-m
            moment_nmm = moment * 1000000  # Convert to N-mm
            
            # Estimate beam depth (span/10 to span/12 rule of thumb)
            effective_depth = span_mm / 10
            overall_depth = effective_depth + 50  # Assuming 50mm cover + bar dia
            
            # Assume width as depth/2 (typical ratio)
            width = overall_depth / 2
            
            # Calculate required steel area
            # Using simplified formula: Ast = M / (0.87 * fy * 0.9 * d)
            ast_required = moment_nmm / (0.87 * fy * 0.9 * effective_depth)
            
            # Minimum steel (0.85% of gross area as per IS 456)
            min_steel = (0.85 / 100) * width * overall_depth
            ast_required = max(ast_required, min_steel)
            
            # Calculate number of bars (assuming 16mm dia bars)
            bar_area = math.pi * (16**2) / 4  # Area of 16mm bar
            num_bars = math.ceil(ast_required / bar_area)
            actual_steel = num_bars * bar_area
            
            # Calculate concrete volume
            concrete_volume = (width * overall_depth * span_mm) / 1000000000  # m³
            
            # Steel weight
            steel_density = self.steel_grades[steel_grade]['density']  # kg/m³
            steel_length = span * num_bars  # Main bars length
            steel_volume = (actual_steel * steel_length) / 1000000  # m³
            steel_weight = steel_volume * steel_density  # kg
            
            return {
                'beam_width': round(width, 0),
                'beam_depth': round(overall_depth, 0),
                'effective_depth': round(effective_depth, 0),
                'moment': round(moment, 2),
                'steel_area_required': round(ast_required, 0),
                'steel_area_provided': round(actual_steel, 0),
                'num_bars': num_bars,
                'concrete_volume': round(concrete_volume, 3),
                'steel_weight': round(steel_weight, 2),
                'fck': fck,
                'fy': fy
            }
            
        except Exception as e:
            logging.error(f"Beam calculation error: {str(e)}")
            raise Exception(f"Calculation failed: {str(e)}")

class MaterialEstimator:
    """Calculator for material quantity and cost estimation"""
    
    def calculate_quantities(self, length, width, height, cement_rate, sand_rate, aggregate_rate, steel_rate):
        """Calculate material quantities for a room/building"""
        try:
            # Room/building parameters
            floor_area = length * width  # m²
            wall_area = 2 * (length + width) * height  # m² (assuming standard walls)
            
            # Concrete volume calculations (assuming RCC structure)
            slab_thickness = 0.15  # 150mm slab
            beam_volume = floor_area * 0.03  # Approximate beam volume
            column_volume = floor_area * 0.02  # Approximate column volume
            footing_volume = floor_area * 0.05  # Approximate footing volume
            
            total_concrete_volume = floor_area * slab_thickness + beam_volume + column_volume + footing_volume
            
            # Material quantities per m³ of concrete (standard mix ratios)
            # For M25 grade concrete (1:1:2)
            cement_bags_per_m3 = 8.5  # bags of 50kg each
            sand_per_m3 = 0.45  # m³
            aggregate_per_m3 = 0.9  # m³
            steel_per_m3 = 80  # kg (typical for residential buildings)
            
            # Total material quantities
            cement_bags = total_concrete_volume * cement_bags_per_m3
            sand_volume = total_concrete_volume * sand_per_m3
            aggregate_volume = total_concrete_volume * aggregate_per_m3
            steel_weight = total_concrete_volume * steel_per_m3
            
            # Brick work for walls (assuming 230mm thick brick walls)
            brick_volume = wall_area * 0.23  # m³
            bricks_required = brick_volume * 500  # 500 bricks per m³
            mortar_volume = brick_volume * 0.3  # 30% mortar
            
            # Additional cement and sand for brick work
            cement_bags_brickwork = mortar_volume * 5.5  # bags
            sand_brickwork = mortar_volume * 1.0  # m³
            
            # Total quantities
            total_cement_bags = cement_bags + cement_bags_brickwork
            total_sand_volume = sand_volume + sand_brickwork
            
            # Cost calculations
            cement_cost = total_cement_bags * cement_rate
            sand_cost = total_sand_volume * sand_rate
            aggregate_cost = aggregate_volume * aggregate_rate
            steel_cost = steel_weight * steel_rate
            brick_cost = bricks_required * 8  # ₹8 per brick
            
            total_material_cost = cement_cost + sand_cost + aggregate_cost + steel_cost + brick_cost
            
            # Add labor cost (approximately 40% of material cost)
            labor_cost = total_material_cost * 0.4
            total_cost = total_material_cost + labor_cost
            
            return {
                'dimensions': {
                    'length': length,
                    'width': width,
                    'height': height,
                    'floor_area': round(floor_area, 2),
                    'wall_area': round(wall_area, 2)
                },
                'concrete': {
                    'volume': round(total_concrete_volume, 3),
                    'cement_bags': round(total_cement_bags, 1),
                    'sand_volume': round(total_sand_volume, 2),
                    'aggregate_volume': round(aggregate_volume, 2),
                    'steel_weight': round(steel_weight, 2)
                },
                'brickwork': {
                    'brick_volume': round(brick_volume, 3),
                    'bricks_required': round(bricks_required, 0),
                    'mortar_volume': round(mortar_volume, 3)
                },
                'costs': {
                    'cement_cost': round(cement_cost, 2),
                    'sand_cost': round(sand_cost, 2),
                    'aggregate_cost': round(aggregate_cost, 2),
                    'steel_cost': round(steel_cost, 2),
                    'brick_cost': round(brick_cost, 2),
                    'total_material_cost': round(total_material_cost, 2),
                    'labor_cost': round(labor_cost, 2),
                    'total_cost': round(total_cost, 2)
                }
            }
            
        except Exception as e:
            logging.error(f"Material estimation error: {str(e)}")
            raise Exception(f"Estimation failed: {str(e)}")

class ProjectScheduler:
    """Simple project scheduler with Gantt chart generation"""
    
    def create_schedule(self, tasks_data):
        """Create a project schedule from task data"""
        try:
            # Start date (today)
            start_date = datetime.now()
            
            schedule = []
            current_date = start_date
            
            for i, task in enumerate(tasks_data):
                task_start = current_date
                task_end = current_date + timedelta(days=task['duration'] - 1)
                
                schedule.append({
                    'id': i + 1,
                    'name': task['name'],
                    'duration': task['duration'],
                    'start_date': task_start.strftime('%Y-%m-%d'),
                    'end_date': task_end.strftime('%Y-%m-%d'),
                    'start_day': (task_start - start_date).days + 1,
                    'width': task['duration'] * 20  # Width for visualization
                })
                
                # Next task starts after current task ends
                current_date = task_end + timedelta(days=1)
            
            # Project summary
            total_duration = (current_date - start_date).days
            project_end = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
            
            return {
                'tasks': schedule,
                'project_start': start_date.strftime('%Y-%m-%d'),
                'project_end': project_end,
                'total_duration': total_duration,
                'total_tasks': len(schedule)
            }
            
        except Exception as e:
            logging.error(f"Scheduling error: {str(e)}")
            raise Exception(f"Scheduling failed: {str(e)}")
