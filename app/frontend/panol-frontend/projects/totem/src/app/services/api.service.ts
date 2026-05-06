import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface Resource {
  id: string;
  nombre: string;
  categoria: string;
  stockTotal: number;
  stockDisponible: number;
}

export interface RequestItem {
  recursoId: string;
  cantidad: number;
}

export interface Request {
  id: string;
  usuarioId: string;
  usuarioNombre?: string; // agregado en cliente
  items: RequestItem[];
  estado: string;
  createdAt: string;
}

export interface Loan {
  id: string;
  requestId: string;
  usuarioId: string;
  estado: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  resources = signal<Resource[]>([]);
  requests = signal<Request[]>([]);
  loans = signal<Loan[]>([]);

  async loadInventory() {
    const data = await firstValueFrom(this.http.get<Resource[]>('/api/inventory/resources'));
    this.resources.set(data);
  }

  async loadRequests() {
    const data = await firstValueFrom(this.http.get<Request[]>('/api/requests'));
    // Enriquecer con nombres de usuario y recursos
    const usersToFetch = [...new Set(data.map(r => r.usuarioId))];
    let users: any[] = [];
    if (usersToFetch.length > 0) {
      users = await firstValueFrom(this.http.post<any[]>('/api/auth/users/batch', { ids: usersToFetch })).catch(() => []);
    }
    
    if (this.resources().length === 0) await this.loadInventory();
    
    const enriched = data.map(req => ({
      ...req,
      usuarioNombre: users.find(u => u.id === req.usuarioId)?.nombre || req.usuarioId
    }));
    this.requests.set(enriched);
  }

  async loadLoans() {
    const data = await firstValueFrom(this.http.get<Loan[]>('/api/loans'));
    this.loans.set(data);
  }

  async materialize(requestId: string): Promise<void> {
    await firstValueFrom(this.http.post(`/api/loans/${requestId}/materialize`, {}));
    await this.loadRequests();
    await this.loadLoans();
  }

  async returnLoan(loanId: string, items: { recursoId: string; cantidad: number; estado: string }[]): Promise<void> {
    await firstValueFrom(this.http.post(`/api/loans/${loanId}/return`, { items }));
    await this.loadLoans();
  }

  getResourceName(id: string): string {
    return this.resources().find(r => r.id === id)?.nombre || id;
  }
}
