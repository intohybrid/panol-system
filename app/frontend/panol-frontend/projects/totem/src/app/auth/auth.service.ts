import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

export interface AuthUser {
  id: string;
  documento: string;
  nombre: string;
  role: 'ALUMNO' | 'DOCENTE' | 'PANOLERO' | 'COORDINADOR' | 'JEFE';
  status: string;
}

const TOKEN_KEY = 'panol.totem_token';
const USER_KEY = 'panol.totem_user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  currentUser = signal<AuthUser | null>(this.loadStoredUser());
  isAuthenticated = computed(() => !!this.currentUser());

  async loginByPin(pin: string): Promise<void> {
    const res = await firstValueFrom(
      this.http.post<{ accessToken: string; user: AuthUser }>('/api/auth/login-pin', { pin }),
    );
    localStorage.setItem(TOKEN_KEY, res.accessToken);
    localStorage.setItem(USER_KEY, JSON.stringify(res.user));
    this.currentUser.set(res.user);
    this.router.navigate(['/dashboard']);
  }

  async verifyPin(pin: string): Promise<boolean> {
    try {
      await firstValueFrom(this.http.post('/api/auth/verify-pin', { pin }));
      return true;
    } catch {
      return false;
    }
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.currentUser.set(null);
    this.router.navigate(['/pin']);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  private loadStoredUser(): AuthUser | null {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }
}
