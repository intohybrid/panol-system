import { Routes } from '@angular/router';
import { authGuard } from './auth/auth.guard';

export const routes: Routes = [
  { path: 'pin', loadComponent: () => import('./pin-login/pin-login.component').then(m => m.PinLoginComponent) },
  {
    path: '',
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent) },
      { path: 'return/:id', loadComponent: () => import('./return-loan/return-loan.component').then(m => m.ReturnLoanComponent) },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    ],
  },
  { path: '**', redirectTo: 'pin' },
];
