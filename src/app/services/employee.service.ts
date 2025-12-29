import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, throwError, timeout } from 'rxjs';
import { environment } from '../../environments/environment';
import { Employee } from '../interfaces/employee.model';

@Injectable({ providedIn: 'root' })
export class EmployeeService {
  constructor(private http: HttpClient) {}

  private buildUrl(path: string): string {
    if (environment.apiUrl) {
      return `${environment.apiUrl}${path}`;
    }
    return path; // Use relative path for proxied requests
  }

  getAll(): Observable<Employee[]> {
    const url = this.buildUrl('/rh/get-all-employees');
    console.log('Fetching employees from:', url);
    return this.http.get<Employee[]>(url).pipe(
      timeout(10000), // 10 second timeout
      catchError((err: HttpErrorResponse) => {
        console.error('Employee fetch error:', err);
        return throwError(() => new Error(this.msg(err, 'Get all employees')));
      })
    );
  }

  create(employee: EmployeeCreatePayload): Observable<Employee> {
    const url = this.buildUrl('/rh/create-employee');
    return this.http.post<Employee>(url, employee).pipe(
      catchError((err: HttpErrorResponse) => {
        return throwError(() => new Error(this.msg(err, 'Create employee')));
      })
    );
  }

  private msg(error: HttpErrorResponse, ctx: string): string {
    if (error.status === 0) return `${ctx}: Cannot reach API`;

    // Handle validation errors (422)
    if (error.status === 422 && error.error?.detail) {
      const details = error.error.detail;
      if (Array.isArray(details)) {
        const messages = details.map((err: any) => {
          const field = err.loc?.join('.') || 'unknown';
          return `${field}: ${err.msg}`;
        });
        return `${ctx}: ${messages.join(', ')}`;
      }
    }

    const detail = (error.error as any)?.detail;
    if (typeof detail === 'string') {
      return `${ctx}: ${detail}`;
    } else if (detail) {
      return `${ctx}: ${JSON.stringify(detail)}`;
    }

    return `${ctx} failed (${error.status})`;
  }
}

export interface EmployeeCreatePayload {
  name: string;
  email: string;
  phone_number: string;
  gender_id: number;
  date_of_birth: string; // yyyy-MM-dd
  zip_code: string;
  location: string;
  marital_status_id: number;
  num_children: number;
  hire_date: string; // yyyy-MM-dd
  contract_type_id: number;
  department_id: number;
  role_id: number;
}
