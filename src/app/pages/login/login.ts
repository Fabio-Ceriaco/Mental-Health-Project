import { ProfileService } from './../../services/profile.service';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectorRef, Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LoginService } from '../../services/login.service';
import { Router } from '@angular/router';
import { RegisterModal } from '../../components/register-modal/register-modal';
import { Rgpd } from '../../components/rgpd/rgpd';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RegisterModal, Rgpd],
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
})
export default class Login {
  email: string = '';
  password: string = '';
  roleUser: string = '';
  roleAdmin: string = '';
  roleExecutive: string = '';
  loginError: string = '';
  registerError: string = '';
  registerSuccess: string = '';
  showRegisterModal: boolean = false;
  rgpdOpened: boolean = false;
  consentGiven: boolean = false;

  constructor(
    private loginService: LoginService,
    private router: Router,
    private profileService: ProfileService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    if (this.loginService.obterToken()) {
      this.router.navigate(['employee-dashboard']);
    }
  }

  login() {
    this.loginError = ''; // limpa mensagens anteriores

    this.loginService.login(this.email, this.password).subscribe({
      next: (res: any) => {
        this.loginService.salvarToken(res.access_token);
        this.loginService.salvarUser(res.utilizador);
        this.loginService.salvarEmployee(res.employee);

        console.log('Token:', res.access_token); // ← DEBUG
        console.log('User:', res.utilizador);
        console.log('Employee:', res.employee);
        console.log('Employee Role Name:', res.employee.role_name);
        if (res.employee.role_name === 'User') {
          this.router.navigate(['/employee-dashboard']);
        } else if (res.employee.role_name === 'Executive') {
          this.router.navigate(['/rh-dashboard']);
        } else {
          this.router.navigate(['/login']); // Default route
        }
      },
      error: (err: HttpErrorResponse) => {
        this.loginError = 'Credenciais inválidas. Por favor, tente novamente.';
        this.cdr.detectChanges();

        setTimeout(() => {
          this.loginError = '';
          this.cdr.detectChanges();
        }, 5000);
      },
    });
  }

  openRgpd() {
    this.rgpdOpened = true;
  }

  // Handle consent from RGPD component
  onConsentSelected(consent: boolean) {
    this.rgpdOpened = false; // Close RGPD modal
    if (consent) {
      // User accepted
      this.consentGiven = true; // Set consent flag
      this.showRegisterModal = true; // Open registration modal
    } else {
      this.consentGiven = false;
    }
  }

  openRegister() {
    this.registerError = '';
    this.registerSuccess = '';
    this.showRegisterModal = true;
  }
  closeRegister() {
    this.registerError = '';
    this.registerSuccess = '';
    this.showRegisterModal = false;
  }
}
