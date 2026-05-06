import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = () => {
  const token = localStorage.getItem('panol.totem_token');
  if (!token) {
    inject(Router).navigate(['/pin']);
    return false;
  }
  return true;
};
