import { LoginService } from '../../services/login.service';
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Router } from '@angular/router';
import { NgOptimizedImage } from '@angular/common';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, NgOptimizedImage],
  templateUrl: './header.html',
  styleUrls: ['./header.css'],
})
export class Header {
  employee: any;
  user: any;
  menuOpen: boolean = false;
  logoUrl: string = 'assets/LogoMH.png';
  logoAlt: string = 'Mental Health Logo';

  constructor(private loginService: LoginService, private router: Router) {
    this.employee = this.loginService.obterEmployee();
    this.user = this.loginService.obterUser();
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
  }

  closeMenu(): void {
    this.menuOpen = false;
  }

  logout() {
    this.loginService.logout();
    this.router.navigate(['/']);
  }
}
