import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface Resource {
  id: string;
  nombre: string;
  categoria: string;
  stock: number;
  stockReservado: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = '/api';

  // Signals para el estado global
  resources = signal<Resource[]>([]);
  requests = signal<any[]>([]);
  loans = signal<any[]>([]);

  async loadInventory() {
    const data = await firstValueFrom(this.http.get<Resource[]>(`${this.baseUrl}/inventory`));
    this.resources.set(data);
  }

  async createRequest(userId: string, items: { recursoId: string, cantidad: number }[]) {
    const req = await firstValueFrom(this.http.post(`${this.baseUrl}/requests`, { userId, items }));
    await this.loadInventory(); // Actualizar stock simulado
    return req;
  }

  async loadRequests() {
    const data = await firstValueFrom(this.http.get<any[]>(`${this.baseUrl}/requests`));
    this.requests.set(data);
  }

  async askAi(prompt: string) {
    return firstValueFrom(this.http.post<any>(`${this.baseUrl}/ai/suggest`, { prompt }));
  }

  async issueLoan(requestId: string, panoleroId: string) {
    return firstValueFrom(this.http.post(`${this.baseUrl}/loans/${requestId}/issue`, { panoleroId }));
  }
}
