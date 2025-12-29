import { Injectable} from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { LoginService } from "../../services/login.service";

@Injectable({
  providedIn: 'root'
})
export class NoAuthGuard implements CanActivate {
  constructor(private loginService: LoginService, private router: Router) {}

  // If the user is authenticated, redirect to dashboard
  canActivate(): boolean {
    const token = this.loginService.obterToken();
    if (token){
      this.router.navigate(['/employee-dashboard']);
      return false;
    }
    return true;
  }
}
