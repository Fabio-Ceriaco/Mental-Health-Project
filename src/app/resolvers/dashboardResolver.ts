import { Injectable } from '@angular/core';
import { Resolve } from '@angular/router';
import { Observable, of } from 'rxjs';
import { DashboardService } from '../services/dashboard.service';
import { LoginService } from '../services/login.service';
import { catchError, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class DashboardResolver implements Resolve<any> {
  constructor(private dashboardService: DashboardService, private loginService: LoginService) {}

  resolve(): Observable<any> {
    const employeeId = this.loginService.employee_Id();
    if (!employeeId) {
      console.warn('No logged in employee ID found'); // Log warning if no employee ID
      return of(null); // Return observable of null
    }

    console.log(`[DashboardResolver] Resolving dashboard for employee: ${employeeId}`);

    return this.dashboardService.getEmployeeDashboard(employeeId).pipe(
      tap((dashboardData) => {
        console.log('Dashboard data fetched successfully:', dashboardData);
      }),
      catchError((error) => {
        console.error('Dashboard resolver error - Full details:', {
          message: error.message,
          status: error.status,
          statusText: error.statusText,
          url: error.url,
          error: error.error,
        });
        return of(null); // Return observable of null on error
      })
    );
  }
}
