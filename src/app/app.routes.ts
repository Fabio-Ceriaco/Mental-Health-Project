import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { Home } from './pages/home/home';
import { NoAuthGuard } from './core/guards/no-auth.guard';
import { AssessmentResolver } from './resolvers/assessmentResolver';
import { DashboardResolver } from './resolvers/dashboardResolver';
import { EmpProfileResolver } from './resolvers/emp_profileResolver';

export const routes: Routes = [
  { path: '', component: Home, canActivate: [NoAuthGuard] },
  { path: 'login', loadComponent: () => import('./pages/login/login'), canActivate: [NoAuthGuard] },
  {
    path: 'employee-dashboard',
    loadComponent: () => import('./pages/employee/dashboard/dashboard'),
    resolve: { dashboardData: DashboardResolver },
    canActivate: [authGuard],
  },
  {
    path: 'new-evaluation',
    loadComponent: () => import('./pages/employee/new-evaluation/new-evaluation'),
    resolve: { questions: AssessmentResolver },
    canActivate: [authGuard],
  },
  {
    path: 'profile',
    loadComponent: () => import('./pages/employee/profile/profile'),
    resolve: { profileData: EmpProfileResolver },
    canActivate: [authGuard],
  },
  {
    path: 'helper',
    loadComponent: () => import('./pages/employee/helper/helper'),
    canActivate: [authGuard],
  },
  {
    path: 'rh-dashboard',
    loadComponent: () => import('./pages/rh/rh-dashboard/rh-dashboard'),
    canActivate: [authGuard],
  },
  {
    path: 'complete-assessments',
    loadComponent: () => import('./pages/rh/complete-assessments/complete-assessments'),
    canActivate: [authGuard],
  },
  {
    path: 'alerts-rh',
    loadComponent: () => import('./pages/rh/alerts-rh/alerts-rh'),
    canActivate: [authGuard],
  },
  {
    path: 'department-metrics',
    loadComponent: () => import('./pages/rh/department-metrics/department-metrics'),
    canActivate: [authGuard],
  },
  {
    path: 'ia-plans',
    loadComponent: () => import('./pages/rh/ia-plans/ia-plans'),
    canActivate: [authGuard],
  },
  {
    path: '**',
    redirectTo: '',
  },
];
