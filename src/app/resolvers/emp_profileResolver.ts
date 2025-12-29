import { Injectable } from '@angular/core';
import { Resolve } from '@angular/router';
import { forkJoin, Observable, of } from 'rxjs';
import { ProfileService } from '../services/profile.service';
import { LoginService } from '../services/login.service';

@Injectable({
  providedIn: 'root',
})
export class EmpProfileResolver implements Resolve<any> {
  constructor(private loginService: LoginService, private profileService: ProfileService) {}

  //--------- Resolve Method ---------//

  // Fetch employee profile data before activating the profile route
  resolve(): Observable<any> {
    return forkJoin({
      profile: this.profileService.getProfile(),
      options: this.profileService.getOptions(),
    });
  }
}
