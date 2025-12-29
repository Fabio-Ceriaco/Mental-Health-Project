#======================================================================================================
# script to generate SQL for employee_responses table
#======================================================================================================


# import random
# import csv
# from datetime import datetime, timedelta
# import math

# NUM_EMPLOYEES = 850
# QUESTIONS_PER_ASSESSMENT = 40
# ASSESSMENTS = [1, 2]
# ASSESSMENTS_PER_YEAR = 4
# YEARS = 4
# TOTAL_EVALUATIONS = ASSESSMENTS_PER_YEAR * YEARS

# now = datetime.now()
# auto_id = 1

# DIMENSIONS = {
#     "anxiety": range(1, 11),
#     "depression": range(11, 21),
#     "stress": range(21, 31),
#     "burnout": range(31, 41),
# }

# def clamp(value, min_value=0, max_value=4):
#     return max(min_value, min(max_value, value))

# def bounded_normal(mean, std=0.6):
#     return random.gauss(mean, std)

# with open("employee_response.csv", "w", newline="", encoding="utf-8") as f:
#     writer = csv.writer(f)

#     writer.writerow([
#         "id",
#         "employee_id",
#         "assessment_id",
#         "question_id",
#         "answer_value",
#         "created_at",
#         "updated_at",
#     ])

#     for emp_id in range(1, NUM_EMPLOYEES + 1):

#         # 🧠 Perfil psicológico realista por dimensão
#         profile = {
#             "anxiety": random.uniform(1.5, 3.8),
#             "depression": random.uniform(1.2, 3.5),
#             "stress": random.uniform(1.8, 4.0),
#             "burnout": random.uniform(1.0, 3.2),
#         }

#         # 📈 Tendência independente por dimensão
#         trends = {
#             d: random.uniform(-0.6, 0.7)
#             for d in DIMENSIONS
#         }

#         for eval_index in range(TOTAL_EVALUATIONS):

#             assessment_id = ASSESSMENTS[eval_index % 2]
#             base_date = now - timedelta(days=90 * eval_index)

#             # 🔀 eventos reais (ex: crise, melhoria, pico de stress)
#             event_impact = random.choice([0, 0, 0, random.uniform(-1.0, 1.2)])

#             for dim, questions in DIMENSIONS.items():

#                 time_factor = trends[dim] * math.sin(eval_index / 3)
#                 dimension_shift = profile[dim] + time_factor + event_impact

#                 for q in questions:

#                     noise = bounded_normal(0, 0.5)

#                     raw_score = dimension_shift + noise
#                     final_score = round(clamp(raw_score))

#                     response_datetime = base_date.replace(
#                         hour=random.randint(8, 18),
#                         minute=random.randint(0, 59),
#                         second=random.randint(0, 59)
#                     ) + timedelta(seconds=q)

#                     writer.writerow([
#                         auto_id,
#                         emp_id,
#                         assessment_id,
#                         q,
#                         final_score,
#                         response_datetime.isoformat(),
#                         response_datetime.isoformat()
#                     ])

#                     auto_id += 1

# print("✅ CSV gerado com distribuição psicológica realista e analisável.")










#======================================================================================================
# script to populate assessment_result table
#======================================================================================================

# from datetime import datetime
# from sqlalchemy.orm import Session
# from app.models.assessment_result import AssessmentResult
# from app.models.employeeAssessmentAnswers import EmployeeAssessmentAnswers
# from app.models.assessment_answers import AssessmentAnswers
# from app.database.db_conn import SessionLocal

# RISK_THRESHOLDS = [
#     (1.5, 1),
#     (3.5, 2),
#     (4.5, 3),
#     (5.0, 4)
# ]

# def map_score_to_risk(score: float) -> int:
#     for threshold, risk_id in RISK_THRESHOLDS:
#         if score <= threshold:
#             return risk_id
#     return 4

# def generate_assessment_results():
#     db: Session = SessionLocal()

#     # Map de answerID para answerValue
#     answers_map = {a.assessmentAnswersID: a.answerValue for a in db.query(AssessmentAnswers).all()}

#     employees_ids = [r[0] for r in db.query(EmployeeAssessmentAnswers.employeeID).distinct()]
    
#     for emp_id in employees_ids:
#         assessments = db.query(EmployeeAssessmentAnswers.assessmentID)\
#                         .filter(EmployeeAssessmentAnswers.employeeID == emp_id)\
#                         .distinct()
#         for assessment in assessments:
#             assessment_id = assessment[0]
#             responses = db.query(EmployeeAssessmentAnswers)\
#                         .filter(EmployeeAssessmentAnswers.employeeID == emp_id,
#                                 EmployeeAssessmentAnswers.assessmentID == assessment_id)\
#                         .all()
#             if not responses:
#                 continue

#             # Detalhado por pergunta
#             for resp in responses:
#                 answer_value = answers_map.get(resp.assessmentAnswersID, None)
#                 if answer_value is None:
#                     continue  # ignora respostas inválidas
#                 detailed_result = AssessmentResult(
#                     assessmentID=assessment_id,
#                     userID=emp_id,
#                     assessmentQuestionID=resp.assessmentQuestionsID,
#                     assessmentAnswerID=resp.assessmentAnswersID,
#                     riskLevelID=map_score_to_risk(answer_value),
#                     createdAt=datetime.now(),
#                     updatedAt=datetime.now()
#                 )
#                 db.add(detailed_result)

#             # Resumo por questionário
#             total_score = sum(answers_map.get(r.assessmentAnswersID, 0) for r in responses)
#             avg_score = total_score / len(responses)
#             summary_result = AssessmentResult(
#                 assessmentID=assessment_id,
#                 userID=emp_id,
#                 assessmentQuestionID=None,
#                 assessmentAnswerID=None,
#                 riskLevelID=map_score_to_risk(avg_score),
#                 createdAt=datetime.now(),
#                 updatedAt=datetime.now()
#             )
#             db.add(summary_result)

#     db.commit()
#     db.close()
#     print("✅ Assessment_Results populada com sucesso.")

# if __name__ == "__main__":
#     generate_assessment_results()

#======================================================================================
# script to populate metric_status table
#======================================================================================

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from datetime import datetime
# from app.models.metric_status import MetricStatus

# # Configurar ligação à base
# engine = create_engine("sqlite:///mental_health.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# # Status predefinidos
# statuses = ["Normal", "Elevado", "Alto", "Crítico"]

# now = datetime.now()

# for idx, name in enumerate(statuses, start=1):
#     status = MetricStatus(
#         statusID=idx,
#         metricName=name
#     )
#     session.add(status)

# session.commit()
# session.close()

# print("✅ Metric_Status populada com sucesso.")



#==============================================================================
# script to populate question_metric_type table
#==============================================================================

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from datetime import datetime
# from app.models.assessment_questions import AssessmentQuestions
# from app.models.question_metric_type import QuestionMetricType

# engine = create_engine("sqlite:///mental_health.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# now = datetime.now()

# questions = session.query(AssessmentQuestions).all()

# metric_types = ["anxiety", "depression", "stress", "burnout"]

# for idx, question in enumerate(questions, start=1):
#     metric_type = metric_types[idx % len(metric_types)]

#     qmt = QuestionMetricType(
#         assessmentQuestionsID=question.assessmentQuestionsID,  # Garantido que está ligado à sessão
#         metricType=metric_type,
        
#     )
#     session.add(qmt)

# session.commit()
# session.close()
# print("✅ QuestionMetricType populada com sucesso.")

#======================================================================================
# script to populate department_metrics table with realistic data
#======================================================================================

# from sqlalchemy.orm import Session
# from datetime import datetime
# import numpy as np

# from app.models.employees import Employees
# from app.models.assessment_result import AssessmentResult
# from app.models.department_metrics import DepartmentMetrics
# from app.models.metric_status import MetricStatus
# from app.models.question_metric_type import QuestionMetricType


# def populate_department_metrics(db: Session):
#     now = datetime.now()

#     departments = db.query(Employees.departmentID).distinct().all()
#     departments = [d[0] for d in departments]

#     metric_statuses = db.query(MetricStatus).all()
#     status_map = {s.metricName: s.statusID for s in metric_statuses}

#     question_type_map = {
#         q.assessmentQuestionsID: q.metricType
#         for q in db.query(QuestionMetricType).all()
#     }

#     thresholds = {
#         "Normal": 1.5,
#         "Elavado": 2.5,
#         "Alto": 3.2,
#         "Crítico": 5.0
#     }

#     for dept_id in departments:
#         results = (
#             db.query(AssessmentResult)
#             .join(Employees, Employees.employeeID == AssessmentResult.userID)
#             .filter(Employees.departmentID == dept_id)
#             .all()
#         )

#         metrics = {
#             "anxiety": [],
#             "depression": [],
#             "stress": [],
#             "burnout": []
#         }

#         for r in results:
#             metric_type = question_type_map.get(r.assessmentQuestionID)
#             if metric_type and r.assessment_answer:
#                 metrics[metric_type].append(float(r.assessment_answer.answerValue))

#         all_values = (
#             metrics["anxiety"] +
#             metrics["depression"] +
#             metrics["stress"] +
#             metrics["burnout"]
#         )

#         if not all_values:
#             continue

#         anxiety_avg = round(np.mean(metrics["anxiety"]), 2) if metrics["anxiety"] else 0
#         depression_avg = round(np.mean(metrics["depression"]), 2) if metrics["depression"] else 0
#         stress_avg = round(np.mean(metrics["stress"]), 2) if metrics["stress"] else 0
#         burnout_avg = round(np.mean(metrics["burnout"]), 2) if metrics["burnout"] else 0

#         p25 = round(np.percentile(all_values, 25), 2)
#         p50 = round(np.percentile(all_values, 50), 2)
#         p75 = round(np.percentile(all_values, 75), 2)

#         global_avg = (anxiety_avg + depression_avg + stress_avg + burnout_avg) / 4

#         status_name = "Critical"
#         for name, threshold in thresholds.items():
#             if global_avg <= threshold:
#                 status_name = name
#                 break

#         metric_status_id = status_map.get(status_name)

#         dept_metric = DepartmentMetrics(
#             departmentID=dept_id,
#             anxiety_Avg=anxiety_avg,
#             depression_Avg=depression_avg,
#             stress_Avg=stress_avg,
#             burnout_Avg=burnout_avg,
#             percentile25=p25,
#             percentile50=p50,
#             percentile75=p75,
#             metricStatus=metric_status_id,
#             recordedAt=now,
#             createdAt=now,
#             updatedAt=now
#         )

#         db.add(dept_metric)

#     db.commit()
#     return "✅ Department_Metrics com médias + percentis calculados com sucesso."

# from app.database.db_conn import SessionLocal

# if __name__ == "__main__":
#     print("🚀 A iniciar geração de Department_Metrics...")

#     db = SessionLocal()
#     populate_department_metrics(db)
#     db.close()

#     print("✅ Execução finalizada.")





#======================================================================================
# script to populate interventions_actions table
#======================================================================================

# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from datetime import datetime
# from app.models.interventions_actions import InterventionActions
# from app.models.actions import Actions

# engine = create_engine("sqlite:///mental_health.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# now = datetime.now()

# actions = session.query(Actions).all()

# for action in actions:
#     ia = InterventionActions(
#     actionID=action.actionID,
#     createdAt=now,
#     updatedAt=now
#     )
#     session.add(ia)

# session.commit()
# session.close()

# print("✅ Interventions_Actions populada com sucesso.")

#======================================================================================
# script to populate psycologist_interventions table
#======================================================================================

# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from datetime import datetime
# from app.models.psycologist_interv import PsycologistInterv
# from app.models.interventions_actions import InterventionActions
# from app.models.employees import Employees
# import random

# engine = create_engine("sqlite:///mental_health.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# now = datetime.now()

# employees = session.query(Employees).all()
# intervention_actions = session.query(InterventionActions).all()

# for emp in employees:
#     for _ in range(random.randint(1,3)): # Cada funcionário pode ter 1-3 intervenções
#         action = random.choice(intervention_actions)
#         pi = PsycologistInterv(
#         employeeID=emp.employeeID,
#         interventionActionsID=action.interventionActionsID,
#         createdAt=now,
#         updatedAt=now
#         )
#         session.add(pi)

# session.commit()
# session.close()

# print("✅ Psycologist_Interventions populada com sucesso.")


#======================================================================================
# script to populate role_metrics table with realistic data
#======================================================================================


# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from datetime import datetime, date
# import random

# from app.models.role_metrics import RoleMetrics
# from app.models.roles import Role
# from app.models.department_metrics import DepartmentMetrics

# engine = create_engine("sqlite:///mental_health.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# now = datetime.now()
# today = date.today()
# metric_names = ["Anxiety", "Depression", "Stress", "Burnout"]

# roles = session.query(Role).all()
# departments_metrics = session.query(DepartmentMetrics).all()

# if not roles:
#     raise Exception("❌ Tabela Role está vazia.")

# if not departments_metrics:
#     raise Exception("❌ Precisas de preencher Department_Metrics antes.")
# created = 0

# for role in roles:

#     existing = session.query(RoleMetrics).filter(
#         RoleMetrics.roleID == role.roleID
#     ).first()

#     if existing:
#         print(f"ℹ️ Role {role.roleName} já tem métricas. Ignorado.")
#         continue

#     # Seleciona uma métrica de departamento aleatória para basear os scores
#     dept_metric_sample = random.choice(departments_metrics)

#     for metric in metric_names:

#         # Obter valor médio do departamento e converter de DECIMAL para float
#         base_score = float(getattr(dept_metric_sample, f"{metric.lower()}_Avg", 0))

#         # Pequena variação aleatória para diferenciar cargos
#         score = round(min(max(base_score + random.uniform(-0.2, 0.2), 0), 5), 2)

#         description_map = {
#             "Anxiety": f"Nível médio de ansiedade ({score}) associado ao cargo {role.roleName}",
#             "Depression": f"Nível médio de depressão ({score}) associado ao cargo {role.roleName}",
#             "Stress": f"Nível médio de stress ({score}) associado ao cargo {role.roleName}",
#             "Burnout": f"Nível médio de burnout ({score}) associado ao cargo {role.roleName}"
#         }

#         rm = RoleMetrics(
#             roleID=role.roleID,
#             metricName=metric,
#             description=description_map[metric],
#             score=score,
#             recordedAt=today,
#             createdAt=now,
#             updatedAt=now
#         )

#         session.add(rm)
#         created += 1

# session.commit()
# session.close()
# print(f"✅ {created} Role_Metrics criadas com sucesso.")




#======================================================================================
# script creates alerts based on department metrics
#======================================================================================


# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine, func
# from datetime import datetime
# from app.models.alerts import Alerts
# from app.models.alert_type import AlertType
# from app.models.departments import Departments
# from app.models.department_metrics import DepartmentMetrics
# from app.models.employees import Employees
# import random

# # ==============================
# # CONFIGURAÇÃO
# # ==============================

# THRESHOLD = 3 # Pode ajustar depois

# engine = create_engine("sqlite:///mental_health.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# now = datetime.now()

# departments = session.query(Departments).all()
# alert_types = session.query(AlertType).all()

# if not alert_types:
#     raise Exception("❌ Não existem AlertTypes na base de dados.")

# alerts_created = 0

# # ==============================
# # PROCESSAMENTO
# # ==============================

# for dept in departments:
#     metrics = session.query(DepartmentMetrics)\
#     .filter(DepartmentMetrics.departmentID == dept.departmentID)\
#     .order_by(DepartmentMetrics.recordedAt.desc())\
#     .first()

#     if not metrics:
#         print(f"⚠️ Departamento {dept.departmentID} sem métricas.")
#         continue

#     global_avg = (
#         metrics.anxiety_Avg +
#         metrics.depression_Avg +
#         metrics.stress_Avg +
#         metrics.burnout_Avg
#     ) / 4

#     print(f"📊 Dept {dept.departmentID} média global: {round(global_avg, 2)}")

#     if global_avg < THRESHOLD:
#         continue
    
#     employee = session.query(Employees)\
#         .filter(Employees.departmentID == dept.departmentID)\
#         .order_by(func.random())\
#         .first()

#     if not employee:
#         print(f"⚠️ Departamento {dept.departmentID} não tem funcionários.")
#         continue
#     alert_type = random.choice(alert_types)

#     alert = Alerts(
#         alertTypeID=alert_type.alertTypeID,
#         departmentID=dept.departmentID,
#         employeeID=employee.employeeID,
#         message=f"Alerta automático: média global do departamento = {round(global_avg, 2)}",
#         createdAt=now,
#         updatedAt=now
#     )

#     session.add(alert)
#     alerts_created += 1
# # ==============================
# # COMMIT FINAL
# # ==============================

# session.commit()
# session.close()

# print(f"✅ {alerts_created} alerts criados com sucesso.")



#======================================================================================
# script to populate ia_improve_plan table
#======================================================================================

# from sqlalchemy.orm import Session
# from app.database.db_conn import SessionLocal
# from app.models.ia_improve_plan import IAImprovePlan
# from app.models.departments import Departments
# from app.models.actions_department import ActionsDepartment
# from app.models.status import Status


# def seed_ia_improve_plan():
#     db: Session = SessionLocal()
    
#     try:
#         # ✅ Validar dados base
#         departments = db.query(Departments).all()
#         actions = db.query(ActionsDepartment).all()
#         statuses = db.query(Status).all()

#         if not departments:
#             print("❌ Não existem departamentos.")
#             return

#         if not actions:
#             print("❌ Não existem ações de departamento.")
#             return

#         if not statuses:
#             print("❌ Não existem status.")
#             return

#         created = 0

#         for dept in departments:
#             action = actions[dept.departmentID % len(actions)]
#             status = statuses[dept.departmentID % len(statuses)]

#             # ✅ Evitar duplicados
#             exists = db.query(IAImprovePlan).filter_by(
#                 departmentID=dept.departmentID,
#                 actionsDepartmentID=action.actionsDepartmentID
#             ).first()

#             if exists:
#                 continue

#             plan = IAImprovePlan(
#                 departmentID=dept.departmentID,
#                 actionsDepartmentID=action.actionsDepartmentID,
#                 statusID=status.statusID
#             )

#             db.add(plan)
#             created += 1

#         db.commit()
#         print(f"✅ {created} registos de IA_Improve_Plan criados com sucesso.")

#     except Exception as e:
#         db.rollback()
#         print("❌ Erro ao gerar IA_Improve_Plan:", str(e))

#     finally:
#         db.close()


# if __name__ == "__main__":
#     seed_ia_improve_plan()




#======================================================================================
# script to populate ia_impact_eval table
#======================================================================================


# from random import uniform
# from datetime import datetime
# from sqlalchemy.orm import Session

# from app.database.db_conn import SessionLocal
# from app.models.ia_improve_plan import IAImprovePlan
# from app.models.ia_impact_eval import IAImpactEval


# def seed_ia_impact_eval():
#     db: Session = SessionLocal()

#     plans = db.query(IAImprovePlan).all()

#     if not plans:
#         print("❌ Nenhum IA_Improve_Plan encontrado.")
#         return

#     total_created = 0

#     for plan in plans:
#         before = round(uniform(2.5, 4.5), 2)
#         improvement = uniform(0.6, 0.85)
#         after = round(before * improvement, 2)

#         impact = IAImpactEval(
#             planID=plan.improvePlanID,
#             beforeIndex=before,
#             afterIndex=after,
#             avaliationDate=datetime.now()
#         )

#         db.add(impact)
#         total_created += 1

#     db.commit()
#     db.close()

#     print(f"✅ {total_created} IA_Impact_Eval inseridos com sucesso.")
    
# if __name__ == "__main__":
#     seed_ia_impact_eval()




#======================================================================================
# script to populate audit_log table
#======================================================================================

# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from datetime import datetime
# from app.models.audit_log import AuditLog
# from app.models.employees import Employees
# import random

# engine = create_engine("sqlite:///mental_health.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# now = datetime.now()
# employees = session.query(Employees).all()

# for emp in employees:
#     for _ in range(random.randint(1,3)):
#         log = AuditLog(
#         userID=emp.employeeID,
#         action=f"Ação simulada para teste {random.randint(1,100)}",
        
#         )
#         session.add(log)

# session.commit()
# session.close()

# print("✅ Audit_Logs populada com sucesso.")





# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from datetime import datetime
# import random

# from app.models.role_metrics import RoleMetrics
# from app.models.department_metrics import DepartmentMetrics

# engine = create_engine("sqlite:///mental_health.db")
# Session = sessionmaker(bind=engine)
# session = Session()

# metrics = session.query(RoleMetrics).all()
# departments = session.query(DepartmentMetrics).all()

# if not metrics:
#     raise Exception("❌ role_metrics vazio.")

# if not departments:
#     raise Exception("❌ department_metrics vazio.")

# for rm in metrics:
#     dept = random.choice(departments)

#     base_score = float(getattr(dept, f"{rm.metricName.lower()}_Avg", 0))
#     rm.score = round(
#         min(max(base_score + random.uniform(-0.3, 0.3), 0), 5),
#         2
#     )
#     rm.updatedAt = datetime.now()

# session.commit()
# session.close()

# print("✅ Scores atualizados com sucesso.")