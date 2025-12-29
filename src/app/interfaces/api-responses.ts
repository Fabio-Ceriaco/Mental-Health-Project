export interface DashboardResponse {
  per_assessment_results: AssessmentResult[];
  per_dimension: DimensionData[];
  overall: OverallMetrics;
}

export interface AssessmentResult {
  date: string;
  score: number;
  stress: number;
  anxiety: number;
  depression: number;
  burnout: number;
}

export interface DimensionData {
  name: string;
  value: number;
}

export interface OverallMetrics {
  latest_risk_level: number;
  latest_score: number;
  trend: number;
  total_assessments: number;
}

export interface MLPrediction {
  predicted_risk_level: number;
  risk_label?: string;
  confidence?: number;
  probabilities: {
    level_1: number;
    level_2: number;
    level_3: number;
    level_4: number;
    level_5: number;
  };
  contributing_features: Array<{
    feature: string;
    importance: number;
    value: number;
  }>;
}

export interface EmployeeProfile {
  id: number;
  name: string;
  email: string;
  department_id: number;
  role_id: number;
  contract_type_id: number;
  marital_status_id: number;
  gender_id: number;
  birth_date: string;
  hire_date: string;
  children: number;
}

export interface AssessmentTemplate {
  id: number;
  question_id: number;
  text: string;
  dimension: string;
  answer_options: AnswerOption[];
}

export interface AnswerOption {
  id: number;
  text: string;
  score: number;
}

export interface ApiError {
  detail: string;
  status: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  employee: EmployeeProfile;
}
