# # =======================================================================
# # Código para gerar dados fictícios de funcionários e exportar para CSV
# # =======================================================================


# import random
# from faker import Faker
# from datetime import date, datetime, timedelta
# import pandas as pd

# fake = Faker('pt_PT')

# # Parametros

# num_employees = 850
# departments = [1,2,3,4,5,6,7,8]  # departmentID
# roles_weights = [0.1, 0.2, 0.7]  # distribuição de roles
# roles = list(range(1,4))  # roleID 1-12
# genders = [1,2,3,4,5]  # genderID
# marital_statuses = [1,2,3,4,5]  # maritalStatusID
# contract_types = [1,2,3,4,5,6,7,8]  # contractTypeID

# # Código postal e localizações aproximadas de Évora

# zip_codes = ['7000-001', '7000-002','7005-001','7006-001','7004-001','7000-500']
# locations = ['Évora', 'Vendas Novas','Montemor-o-Novo','Redondo','Arraiolos','Estremoz','Reguengos de Monsaraz']


# employees = []

# for i in range(num_employees):
#     gender = random.choice(genders)
#     if gender in [1,5]:  # Masculino ou "Prefiro não informar"
#         name = fake.first_name_male() + " " + fake.last_name()
#     else:  # Feminino, Não Binário, Outro
#         name = fake.first_name_female() + " " + fake.last_name()
#     birth_year = random.randint(datetime.now().year - 68, datetime.now().year - 18)
#     birth_month = random.randint(1,12)
#     birth_day = random.randint(1,28)
#     birthDate = datetime(birth_year, birth_month, birth_day).date()

#     contract_years = random.randint(1,30)
#     contract_date = datetime.now() - timedelta(days=contract_years*365 + random.randint(0,364))
#     contract_date = contract_date.date()

#     zip_code = random.choice(zip_codes)
#     location = random.choice(locations)
#     email_domain = random.choice(['gmail.com','hotmail.com','outlook.com'])
#     email = name.lower().replace(' ','') + str(random.randint(1,99)) + '@' + email_domain

#     marital_status = random.choice(marital_statuses)
#     num_children = 0
#     if marital_status in [2,3,4]:  # Casado(a), União de Facto, Divorciado(a)
#         num_children = random.randint(0,4)
#     departmentID = random.choice(departments)
#     role = random.choices(roles, weights=roles_weights, k=1)[0]
#     contract_type = random.choice(contract_types)

#     phone_number = fake.phone_number()

#     employees.append({
#         'name': name,
#         'email': email,
#         'phoneNumber': phone_number,
#         'genderID': gender,
#         'date_of_birth': birthDate,
#         'zipCode': zip_code,
#         'location': location,
#         'maritalStatus': marital_status,
#         'num_children': num_children,
#         'hire_date': contract_date,
#         'contract_type': contract_type,
#         'department_id': departmentID,
#         'role_id': role,
#         'is_active': 1,
#         'created_at': datetime.now(),
#         'updated_at': datetime.now()
#     })


# # Exportar para CSV para inserção em SQLite

# df = pd.DataFrame(employees)
# df.to_csv('employees_data.csv', index=False)
# print("CSV com 2000 funcionários gerado com sucesso!")

#=======================================================================
# Código para importar dados do CSV para SQLite
#=======================================================================


# import sqlite3
# import csv
# from datetime import datetime

# conn = sqlite3.connect('mental_health.db')
# cursor = conn.cursor()

# with open('APP/employees_data.csv', 'r', encoding='utf-8') as f:
#     reader = csv.DictReader(f)
#     for row in reader:
#         cursor.execute("""
#             Insert INTO employee (
#                 name, email, phone_number, gender_id, date_of_birth, zip_code,
#                 location, marital_status_id, num_children, hire_date,
#                 contract_type_id, department_id, role_id, is_active, created_at, updated_at
#             ) VALUES (
#                 :name, :email, :phone_number, :gender_id, :date_of_birth, :zip_code,
#                 :location, :marital_status_id, :num_children, :hire_date,
#                 :contract_type_id, :department_id, :role_id, :is_active, :created_at, :updated_at
#             )
#         """, {
#             'name': row['name'],
#             'email': row['email'],
#             'phone_number': row['phone_number'],
#             'gender_id': row['gender_id'],
#             'date_of_birth': row['date_of_birth'],
#             'zip_code': row['zip_code'],
#             'location': row['location'],
#             'marital_status_id': row['marital_status_id'],
#             'num_children': row['num_children'],
#             'hire_date': row['hire_date'],
#             'contract_type_id': row['contract_type_id'],
#             'department_id': row['department_id'],
#             'role_id': row['role_id'],
#             'is_active': row['is_active'],
#             'created_at': row['created_at'],
#             'updated_at': row['updated_at']
#         })

# conn.commit()
# conn.close()
# print("Importação concluída com sucesso!")



#=======================================================================
# Código para gerar script SQL de inserts a partir do CSV   
#=======================================================================


# import pandas as pd

# # Caminho do CSV
# csv_file = 'employees_data.csv'
# df = pd.read_csv(csv_file, parse_dates=['birthDate','contractDate','createdAt','updatedAt'])

# with open('employees_inserts.sql', 'w', encoding='utf-8') as f:
#     for index, row in df.iterrows():
#         f.write(f"""
# INSERT INTO Employees (
#     employeeName, employeeEmail, phoneNumber, genderID, birthDate, zipCode,
#     location, maritalStatus, num_children, contractDate,
#     contractType, departmentID, roleID, createdAt, updatedAt, deletedAt
# ) VALUES (
#     '{row['employeeName'].replace("'", "''")}',
#     '{row['employeeEmail']}',
#     '{row['phoneNumber']}',
#     {row['genderID']},
#     '{row['birthDate'].strftime('%Y-%m-%d')}',
#     '{row['zipCode']}',
#     '{row['location'].replace("'", "''")}',
#     {row['maritalStatus']},
#     {row['num_children']},
#     '{row['contractDate'].strftime('%Y-%m-%d')}',
#     {row['contractType']},
#     {row['departmentID']},
#     {row['roleID']},
#     '{row['createdAt'].strftime('%Y-%m-%d %H:%M:%S')}',
#     '{row['updatedAt'].strftime('%Y-%m-%d %H:%M:%S')}',
#     NULL
# );
# """)
# print("Arquivo 'employees_inserts.sql' gerado com sucesso!")


#=======================================================================
# Código para gerar hash de password usando Argon2

# from passlib.context import CryptContext

# # Configuração do contexto
# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# # Password em texto plano
# plain_password = "12345"

# # Gerar hash
# hashed_password = pwd_context.hash(plain_password)

# print(hashed_password)

