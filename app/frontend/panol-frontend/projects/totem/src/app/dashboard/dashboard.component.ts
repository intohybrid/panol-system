import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../services/api.service';
import { AuthService } from '../auth/auth.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  api = inject(ApiService);
  auth = inject(AuthService);
  router = inject(Router);

  async ngOnInit() {
    await this.api.loadRequests();
    await this.api.loadLoans();
  }

  get pendingRequests() {
    return this.api.requests().filter(r => r.estado === 'PENDIENTE');
  }

  get activeLoans() {
    return this.api.loans().filter(l => l.estado === 'ACTIVO');
  }

  async materialize(requestId: string) {
    // Para simplificar, asumimos que el pin no se pide para esto o se pide en la pantalla
    // Podríamos pedir PIN de confirmación, pero según ADR-011 lo reservamos para acciones críticas.
    await this.api.materialize(requestId);
  }

  goToReturn(loanId: string) {
    this.router.navigate(['/return', loanId]);
  }

  logout() {
    this.auth.logout();
  }
}
