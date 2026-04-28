import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = '/api';

  requests = signal<any[]>([]);
  loans = signal<any[]>([]);

  async loadRequests() {
    const data = await firstValueFrom(this.http.get<any[]>(`${this.baseUrl}/requests`));
    this.requests.set(data);
  }

  async loadLoans() {
    const data = await firstValueFrom(this.http.get<any[]>(`${this.baseUrl}/loans`));
    this.loans.set(data);
  }

  async issueLoan(requestId: string, panoleroId: string) {
    const res = await firstValueFrom(this.http.post(`${this.baseUrl}/loans/${requestId}/issue`, { panoleroId }));
    await this.loadRequests(); // Actualizar lista de pendientes
    await this.loadLoans();    // Actualizar lista de préstamos activos
    return res;
  }

  async returnLoan(loanId: string) {
    const res = await firstValueFrom(this.http.post(`${this.baseUrl}/loans/${loanId}/return`, {}));
    await this.loadLoans();
    return res;
  }
}
