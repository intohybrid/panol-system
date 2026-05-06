import { Routes } from '@angular/router';
import { authGuard } from './auth/auth.guard';

export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./login/login.component').then(m => m.LoginComponent) },
  {
    path: '',
    canActivate: [authGuard],
    children: [
      { path: 'catalog', loadComponent: () => import('./catalog/catalog.component').then(m => m.CatalogComponent) },
      { path: 'my-requests', loadComponent: () => import('./my-requests/my-requests.component').then(m => m.MyRequestsComponent) },
      { path: '', redirectTo: 'catalog', pathMatch: 'full' },
    ],
  },
  { path: '**', redirectTo: 'login' },
];

