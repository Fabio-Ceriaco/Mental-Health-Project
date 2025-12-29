import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, tap, catchError, throwError, map, timeout, of } from 'rxjs';
import { LoginService } from './login.service';
import { environment } from '../../environments/environment';
import { DashboardResponse, MLPrediction } from '../interfaces/api-responses';

@Injectable({
  providedIn: 'root', // This makes the service available application-wide
})
export class DashboardService {
  private buildUrl(path: string): string {
    if (environment.apiUrl) {
      return `${environment.apiUrl}${path}`;
    }
    return path; // Use relative path for proxied requests
  }

  constructor(private http: HttpClient, private loginService: LoginService) {}

  getGlobalDashboard(): Observable<any> {
    const url = this.buildUrl('/rh/dashboard/global');
    console.log(`[DashboardService] Fetching global dashboard from: ${url}`);

    return this.http.get<any>(url).pipe(
      tap((res: any) => console.log('Global dashboard data:', res)),
      catchError((error: HttpErrorResponse) => {
        const errorDetails = this.getErrorMessage(error, 'Dashboard Global');
        console.error('Error fetching global dashboard:', errorDetails);
        return throwError(() => new Error(errorDetails));
      })
    );
  }

  getDepartmentMetrics(departmentName: string): Observable<any> {
    const url = this.buildUrl('/rh/dashboard/global');
    console.log(`[DashboardService] Fetching department metrics for: ${departmentName}`);

    return this.http.get<any>(url).pipe(
      map((res: any) => {
        // Filter data for specific department
        const deptData =
          res.latest_per_employee?.filter((emp: any) => emp.department_name === departmentName) ||
          [];

        return {
          employees: deptData,
          department: departmentName,
          count: deptData.length,
        };
      }),
      catchError((error: HttpErrorResponse) => {
        const errorDetails = this.getErrorMessage(error, 'Department Metrics');
        console.error('Error fetching department metrics:', errorDetails);
        return throwError(() => new Error(errorDetails));
      })
    );
  }

  getEmployeeDashboard(employeeId: number | string): Observable<DashboardResponse> {
    const id = Number(employeeId);
    if (!Number.isFinite(id)) {
      return throwError(() => new Error('Employee ID inválido'));
    }

    const url = this.buildUrl(`/employee/dashboard/${id}`);
    console.log(`[DashboardService] Fetching dashboard from: ${url}`);

    return this.http.get<DashboardResponse>(url).pipe(
      tap((res: DashboardResponse) => console.log('Dashboard data fetched:', res)),
      catchError((error: HttpErrorResponse) => {
        const errorDetails = this.getErrorMessage(error, 'Dashboard');
        console.error('Error fetching dashboard:', errorDetails);
        return throwError(() => new Error(errorDetails));
      })
    );
  }

  getMLPrediction(employeeId: number | string): Observable<MLPrediction> {
    const id = Number(employeeId);
    if (!Number.isFinite(id)) {
      return throwError(() => new Error('Employee ID inválido'));
    }

    const url = this.buildUrl(`/ml/predict/employee/${id}`);
    console.log(`[DashboardService] Fetching ML prediction from: ${url}`);

    return this.http.get<any>(url).pipe(
      timeout(15000),
      map((res: any) => {
        const pred = res?.prediction ?? res ?? {};
        const predicted = Number(pred?.predicted_risk_level ?? res?.predicted_risk_level ?? 0);
        const rawProbs = pred?.probabilities ?? res?.probabilities ?? {};
        const probsArr: number[] = Array.isArray(rawProbs) ? rawProbs : [];
        const probsObj = !Array.isArray(rawProbs) && rawProbs ? rawProbs : {};
        const pick = (key: string, idx: number) =>
          typeof probsObj[key] === 'number'
            ? Number(probsObj[key])
            : typeof probsArr[idx] === 'number'
            ? Number(probsArr[idx])
            : 0;

        const probabilities = {
          level_1: pick('Risk Level 1 (No Risk)', 0),
          level_2: pick('Risk Level 2 (Mild Risk)', 1),
          level_3: pick('Risk Level 3 (Moderate Risk)', 2),
          level_4: pick('Risk Level 4 (High Risk)', 3),
          level_5: pick('Risk Level 5 (Critical Risk)', 4),
        };

        const adapted: MLPrediction = {
          predicted_risk_level: predicted,
          probabilities,
          contributing_features: [],
        };
        console.log('ML Prediction adapted:', adapted);
        return adapted;
      }),
      tap((res: MLPrediction) => console.log('ML Prediction fetched:', res)),
      catchError((error: HttpErrorResponse) => {
        const errorDetails = this.getErrorMessage(error, 'ML Prediction');
        console.error('Error fetching ML prediction:', errorDetails);
        return throwError(() => new Error(errorDetails));
      })
    );
  }

  private getErrorMessage(error: HttpErrorResponse, context: string): string {
    if (error.status === 0) {
      return (
        `Cannot connect to API at ${environment.apiUrl}. Please ensure:\n` +
        `  1. Backend is running on ${environment.apiUrl}\n` +
        `  2. API is accessible and not blocked by firewall\n` +
        `  3. Check "ng serve" console for CORS errors`
      );
    }

    if (error.status === 401) {
      return `Unauthorized: Your session has expired. Please log in again.`;
    }

    if (error.status === 403) {
      return `Forbidden: You do not have permission to access this resource.`;
    }

    if (error.status === 404) {
      const detail = error.error?.detail;
      return detail ? `${context}: ${detail}` : `${context} endpoint not found (404).`;
    }

    if (error.status === 500) {
      const detail = error.error?.detail || 'Internal server error';
      return `Server error: ${detail}`;
    }

    if (error.error?.detail) {
      return `${error.error.detail}`;
    }

    return `${context} failed: ${error.statusText || error.message}`;
  }
}
