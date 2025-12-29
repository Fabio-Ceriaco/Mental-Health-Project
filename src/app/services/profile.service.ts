import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { EmployeeProfile } from '../interfaces/api-responses';

@Injectable({
  providedIn: 'root',
})
export class ProfileService {
  constructor(private http: HttpClient) {}

  private buildUrl(path: string): string {
    if (environment.apiUrl) {
      return `${environment.apiUrl}${path}`;
    }
    return path;
  }

  //--------- Profile Methods ---------//

  // Fetch employee profile data
  getProfile(): Observable<EmployeeProfile> {
    const url = this.buildUrl('/employee/profile');
    return this.http.get<EmployeeProfile>(url).pipe(
      catchError((error) => {
        console.error('Error fetching profile:', error);
        return throwError(() => new Error('Failed to load profile data. Please try again.'));
      })
    );
  }

  getOptions(): Observable<any> {
    const url = this.buildUrl('/employee/profile/options');
    return this.http.get<any>(url).pipe(
      catchError((error) => {
        console.error('Error fetching profile options:', error);
        return throwError(() => new Error('Failed to load profile options. Please try again.'));
      })
    );
  }

  // Update employee profile data
  updateProfile(payload: any): Observable<EmployeeProfile> {
    const url = this.buildUrl('/employee/profile');
    return this.http.patch<EmployeeProfile>(url, payload).pipe(
      catchError((error) => {
        console.error('Error updating profile:', error);
        return throwError(() => new Error('Failed to update profile. Please try again.'));
      })
    );
  }
}
