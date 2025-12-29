import pandas as pd
from APP.DATABASE.db_conn import SessionLocal
from APP.MODELS.employee import Employee
from APP.MODELS.assessmentResult import AssessmentResult
from APP.MODELS.question import Question
from datetime import datetime

def analyze_data_quality():
    db = SessionLocal()
    
    print("=" * 80)
    print("DATA QUALITY ANALYSIS REPORT")
    print("=" * 80)
    
    # 1. Employee Data Quality
    print("\n1. EMPLOYEE DATA QUALITY")
    print("-" * 80)
    employees = db.query(Employee).all()
    print(f"Total Employees: {len(employees)}")
    
    # Check missing critical fields
    missing_dob = sum(1 for e in employees if not e.date_of_birth)
    missing_hire_date = sum(1 for e in employees if not e.hire_date)
    missing_department = sum(1 for e in employees if not e.department_id)
    missing_email = sum(1 for e in employees if not e.email)
    
    print(f"  ✓ Missing date_of_birth: {missing_dob} ({missing_dob/len(employees)*100:.1f}%)")
    print(f"  ✓ Missing hire_date: {missing_hire_date} ({missing_hire_date/len(employees)*100:.1f}%)")
    print(f"  ✓ Missing department_id: {missing_department} ({missing_department/len(employees)*100:.1f}%)")
    print(f"  ✓ Missing email: {missing_email} ({missing_email/len(employees)*100:.1f}%)")
    
    # Active vs Inactive
    active = sum(1 for e in employees if e.is_active)
    print(f"  ✓ Active employees: {active}/{len(employees)} ({active/len(employees)*100:.1f}%)")
    
    # 2. Assessment Data Quality
    print("\n2. ASSESSMENT DATA QUALITY")
    print("-" * 80)
    assessments = db.query(AssessmentResult).all()
    print(f"Total Assessments: {len(assessments)}")
    
    missing_score = sum(1 for a in assessments if a.score_percent is None)
    missing_risk = sum(1 for a in assessments if a.risk_level_id is None)
    
    print(f"  ✓ Missing score_percent: {missing_score} ({missing_score/len(assessments)*100:.1f}%)")
    print(f"  ✓ Missing risk_level_id: {missing_risk} ({missing_risk/len(assessments)*100:.1f}%)")
    
    # Score distribution
    scores = [a.score_percent for a in assessments if a.score_percent is not None]
    if scores:
        print(f"  ✓ Score range: {min(scores):.2f} - {max(scores):.2f}")
        print(f"  ✓ Average score: {sum(scores)/len(scores):.2f}")
    
    # 3. Assessment per Employee
    print("\n3. ASSESSMENT COVERAGE")
    print("-" * 80)
    emp_assessment_count = {}
    for a in assessments:
        emp_id = a.employee_id
        emp_assessment_count[emp_id] = emp_assessment_count.get(emp_id, 0) + 1
    
    employees_with_assessments = len(emp_assessment_count)
    print(f"Employees with assessments: {employees_with_assessments}/{len(employees)} ({employees_with_assessments/len(employees)*100:.1f}%)")
    
    if emp_assessment_count:
        assessments_per_emp = list(emp_assessment_count.values())
        print(f"  ✓ Min assessments per employee: {min(assessments_per_emp)}")
        print(f"  ✓ Max assessments per employee: {max(assessments_per_emp)}")
        print(f"  ✓ Avg assessments per employee: {sum(assessments_per_emp)/len(assessments_per_emp):.2f}")
    
    # 4. Questions and Answer Quality
    print("\n4. QUESTIONS AND ANSWERS QUALITY")
    print("-" * 80)
    questions = db.query(Question).all()
    print(f"Total Questions: {len(questions)}")
    
    # 5. Data Distribution Issues
    print("\n5. DATA DISTRIBUTION ANALYSIS")
    print("-" * 80)
    
    if emp_assessment_count:
        employees_single_assessment = sum(1 for count in emp_assessment_count.values() if count == 1)
        print(f"Employees with only 1 assessment: {employees_single_assessment} ({employees_single_assessment/employees_with_assessments*100:.1f}%)")
        
        employees_multiple_assessments = sum(1 for count in emp_assessment_count.values() if count > 1)
        print(f"Employees with multiple assessments: {employees_multiple_assessments} ({employees_multiple_assessments/employees_with_assessments*100:.1f}%)")
    
    # 6. Data Quality Score
    print("\n6. OVERALL DATA QUALITY SCORE")
    print("-" * 80)
    
    quality_score = 100
    
    # Deductions
    if missing_dob > 0:
        quality_score -= min(10, missing_dob/len(employees)*100)
    if missing_hire_date > 0:
        quality_score -= min(10, missing_hire_date/len(employees)*100)
    if missing_department > 0:
        quality_score -= min(5, missing_department/len(employees)*100)
    if employees_single_assessment > employees_multiple_assessments:
        quality_score -= 15  # Not enough temporal data
    if employees_with_assessments < len(employees) * 0.8:
        quality_score -= 20  # Not enough coverage
    
    print(f"Data Quality Score: {quality_score:.1f}/100")
    
    # Recommendations
    print("\n7. RECOMMENDATIONS")
    print("-" * 80)
    
    if missing_dob > 0:
        print(f"  ⚠ Fill in missing date_of_birth for {missing_dob} employees")
    if missing_hire_date > 0:
        print(f"  ⚠ Fill in missing hire_date for {missing_hire_date} employees")
    if missing_department > 0:
        print(f"  ⚠ Assign department for {missing_department} employees")
    if employees_single_assessment > employees_multiple_assessments:
        print(f"  ⚠ Collect more assessments per employee (many have only 1 assessment)")
        print(f"    → This limits trend analysis and model training")
    if employees_with_assessments < len(employees) * 0.8:
        print(f"  ⚠ Conduct assessments for {len(employees) - employees_with_assessments} more employees")
    
    if quality_score >= 80:
        print("\n  ✅ DATA QUALITY IS GOOD!")
    elif quality_score >= 60:
        print("\n  ⚠ DATA QUALITY IS ACCEPTABLE BUT COULD BE IMPROVED")
    else:
        print("\n  ❌ DATA QUALITY NEEDS IMPROVEMENT")
    
    print("\n" + "=" * 80)
    db.close()

if __name__ == "__main__":
    analyze_data_quality()
