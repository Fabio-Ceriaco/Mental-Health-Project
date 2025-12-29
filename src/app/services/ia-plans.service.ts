import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ImpactEvaluation {
  before_index: number;
  after_index: number;
  evaluation_date: string;
}

export interface IAPlan {
  id: number;
  department_id: number;
  department_name: string;
  action_id: number;
  action_name: string;
  action_description: string;
  status_id: number;
  status_name: string;
  created_at: string;
  updated_at: string;
  impact_evaluation?: ImpactEvaluation | null;
}

export interface IAPlansResponse {
  items: IAPlan[];
  total: number;
}

@Injectable({
  providedIn: 'root',
})
export class IAPlansService {
  private apiUrl = `${environment.apiUrl}/rh/ia-plans`;

  constructor(private http: HttpClient) {}

  /**
   * Get all IA improvement plans
   */
  getAllPlans(): Observable<IAPlansResponse> {
    return this.http.get<IAPlansResponse>(this.apiUrl);
  }

  /**
   * Get a specific IA improvement plan by ID
   */
  getPlanById(planId: number): Observable<IAPlan> {
    return this.http.get<IAPlan>(`${this.apiUrl}/${planId}`);
  }

  /**
   * Get all IA improvement plans for a specific department
   */
  getPlansByDepartment(departmentId: number): Observable<IAPlansResponse> {
    return this.http.get<IAPlansResponse>(`${this.apiUrl}/department/${departmentId}`);
  }

  /**
   * Update the status of an IA improvement plan
   */
  updatePlanStatus(planId: number, statusId: number): Observable<IAPlan> {
    return this.http.patch<IAPlan>(`${this.apiUrl}/${planId}/status`, null, {
      params: { status_id: statusId.toString() },
    });
  }

  /**
   * Create an impact evaluation for an IA improvement plan
   */
  createImpactEvaluation(
    planId: number,
    beforeIndex: number,
    afterIndex: number
  ): Observable<ImpactEvaluation> {
    return this.http.post<ImpactEvaluation>(`${this.apiUrl}/${planId}/impact`, null, {
      params: {
        before_index: beforeIndex.toString(),
        after_index: afterIndex.toString(),
      },
    });
  }

  /**
   * Generate AI improvement plans for all departments exceeding threshold
   */
  generateAIPlans(threshold?: number): Observable<any> {
    const url =
      `${environment.apiUrl}/rh/ai-generate-plans` +
      (threshold != null ? `?threshold=${threshold}` : '');
    return this.http.post(url, null);
  }

  /**
   * Evaluate impact of an implemented plan
   */
  evaluatePlanImpact(planId: number, beforeIndex: number, afterIndex: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/rh/ai-evaluate-impact/${planId}`, null, {
      params: {
        before_index: beforeIndex.toString(),
        after_index: afterIndex.toString(),
      },
    });
  }
}
