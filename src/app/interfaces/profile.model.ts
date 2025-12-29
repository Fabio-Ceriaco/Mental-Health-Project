export interface ProfileModel {
  employee_id?: number;
  employee_name: string;
  employee_email: string;
  phone_number: string;
  gender_id?: number;
  birth_date: string; // pode ser Date ou string
  zip_code: string;
  location: string;
  marital_status_id: number;
  num_children: number;
  contract_date: string; // pode ser Date ou string
  contract_type_id: number;
  department_id: number;
  role_id: number;
}
