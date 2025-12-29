export interface Employee {
  id: number;
  name: string;
  email: string;
  phone_number: string;
  gender_id?: number;
  date_of_birth: string;
  zip_code: string;
  location: string;
  marital_status_id: number;
  num_children: number;
  hire_date: string;
  contract_type_id: number;
  department_id: number;
  role_id: number;
  role_name?: string;
}
