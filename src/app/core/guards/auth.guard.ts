import {inject} from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';


export const authGuard: CanActivateFn = () => { // Auth Guard to protect routes
  const router = inject(Router); // Inject Router
  const isBrowser = typeof window !== 'undefined' && window.localStorage; // Check if running in browser
  const token = isBrowser ? localStorage.getItem('access_token') : null; // Get token from local storage

  if (!token){ // If no token, redirect to login
    router.navigate(['/']);
    return false;
  }
  return true; // If token exists, allow access
}
