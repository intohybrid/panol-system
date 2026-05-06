import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = () => {
  const token = localStorage.getItem('panol.access_token');
  if (!token) {
    inject(Router).navigate(['/login']);
    return false;
  }
  return true;
};
