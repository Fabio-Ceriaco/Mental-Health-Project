import random
from datetime import datetime, timedelta
from APP.DATABASE.db_conn import SessionLocal
from APP.MODELS.employee import Employee
from APP.MODELS.assessmentResult import AssessmentResult
from APP.MODELS.risk_level import RiskLevel
import json

def generate_synthetic_assessments():
    """
    Generate synthetic follow-up assessments for employees to create temporal data.
    This allows the ML model to detect trends.
    """
    db = SessionLocal()
    
    print("=" * 80)
    print("GENERATING SYNTHETIC FOLLOW-UP ASSESSMENTS")
    print("=" * 80)
    
    # Get all employees
    employees = db.query(Employee).all()
    
    # Get risk levels
    risk_levels = db.query(RiskLevel).all()
    risk_level_map = {rl.name: rl.id for rl in risk_levels}
    
    print(f"\nProcessing {len(employees)} employees...")
    print("Generating 2-3 follow-up assessments per employee...\n")
    
    new_assessments = []
    
    for emp in employees:
        # Get existing assessments
        existing_assessments = db.query(AssessmentResult).filter(
            AssessmentResult.employee_id == emp.id
        ).order_by(AssessmentResult.created_at).all()
        
        if not existing_assessments:
            continue
        
        last_assessment = existing_assessments[-1]
        last_score = last_assessment.score_percent
        last_details = last_assessment.details_json
        
        # Parse last details
        if isinstance(last_details, str):
            try:
                last_details = json.loads(last_details)
            except:
                last_details = {}
        
        # Generate 2-3 follow-up assessments with realistic trends
        num_follow_ups = random.randint(2, 3)
        
        for i in range(1, num_follow_ups + 1):
            # Create date 1-3 months after last assessment
            days_offset = random.randint(30, 90) * i
            new_date = last_assessment.created_at + timedelta(days=days_offset)
            
            # Generate score with random trend
            trend_direction = random.choice(['improving', 'worsening', 'stable'])
            
            if trend_direction == 'improving':
                score_change = random.uniform(2, 8)  # Improvement
            elif trend_direction == 'worsening':
                score_change = random.uniform(-8, -2)  # Worsening
            else:
                score_change = random.uniform(-2, 2)  # Stable
            
            new_score = max(20, min(85, last_score + score_change))  # Keep within reasonable bounds
            
            # Generate dimension data
            per_dimension = {
                "stress": {
                    "score": round(random.uniform(20, 95), 2),
                    "percent": round(random.uniform(10, 90), 2)
                },
                "anxiety": {
                    "score": round(random.uniform(15, 90), 2),
                    "percent": round(random.uniform(5, 85), 2)
                },
                "depression": {
                    "score": round(random.uniform(10, 85), 2),
                    "percent": round(random.uniform(5, 80), 2)
                },
                "burnout": {
                    "score": round(random.uniform(20, 90), 2),
                    "percent": round(random.uniform(10, 85), 2)
                }
            }
            
            details_json = {
                "dimensions": ["stress", "anxiety", "depression", "burnout"],
                "per_dimension": per_dimension,
                "total_questions": 90
            }
            
            # Determine risk level based on score
            if new_score < 35:
                risk_level_id = risk_level_map.get("Sem risco", 1)
            elif new_score < 45:
                risk_level_id = risk_level_map.get("Risco leve", 2)
            elif new_score < 55:
                risk_level_id = risk_level_map.get("Risco moderado", 3)
            elif new_score < 70:
                risk_level_id = risk_level_map.get("Risco elevado", 4)
            else:
                risk_level_id = risk_level_map.get("Risco crítico", 5)
            
            new_assessment = AssessmentResult(
                employee_id=emp.id,
                score_total=round(new_score * 0.9),  # Slightly lower total
                score_percent=round(new_score, 2),
                risk_level_id=risk_level_id,
                details_json=json.dumps(details_json),
                created_at=new_date
            )
            
            new_assessments.append(new_assessment)
    
    # Insert all new assessments
    print(f"Inserting {len(new_assessments)} new assessments into database...\n")
    
    try:
        db.add_all(new_assessments)
        db.commit()
        print(f"✅ Successfully added {len(new_assessments)} synthetic assessments!")
        print("\nNEW DATA STRUCTURE:")
        print("-" * 80)
        
        # Recalculate statistics
        employees = db.query(Employee).all()
        assessments = db.query(AssessmentResult).all()
        
        emp_assessment_count = {}
        for a in assessments:
            emp_id = a.employee_id
            emp_assessment_count[emp_id] = emp_assessment_count.get(emp_id, 0) + 1
        
        assessments_per_emp = list(emp_assessment_count.values())
        
        print(f"Total Assessments: {len(assessments)}")
        print(f"Min assessments per employee: {min(assessments_per_emp)}")
        print(f"Max assessments per employee: {max(assessments_per_emp)}")
        print(f"Avg assessments per employee: {sum(assessments_per_emp)/len(assessments_per_emp):.2f}")
        
        employees_with_trends = sum(1 for count in assessments_per_emp if count > 1)
        print(f"Employees with multiple assessments: {employees_with_trends}/{len(employees)} ({employees_with_trends/len(employees)*100:.1f}%)")
        
        print("\n" + "=" * 80)
        print("✅ SYNTHETIC DATA GENERATION COMPLETE!")
        print("=" * 80)
        print("\n🔄 Next step: Retrain the ML model with the new temporal data:")
        print("   python3 -m APP.ml.train")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error inserting assessments: {e}")
    
    db.close()

if __name__ == "__main__":
    generate_synthetic_assessments()
