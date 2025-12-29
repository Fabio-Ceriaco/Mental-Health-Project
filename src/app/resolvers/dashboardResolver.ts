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
      return of(null); // Return observable of null
    }

    return this.dashboardService.getEmployeeDashboard(employeeId).pipe(
      catchError((error) => {
        console.error('Dashboard resolver error:', error.message);
        return of(null); // Return observable of null on error
      })
    );
  }
}
