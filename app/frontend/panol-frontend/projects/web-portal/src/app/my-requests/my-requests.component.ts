import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-my-requests',
  standalone: true,
  template: `
<div class="page-layout">
  <div class="page-header">
    <div class="header-left">
      <button class="btn-secondary back-btn" (click)="back()">← Volver al Catálogo</button>
      <h1 class="page-title">Historial de Solicitudes</h1>
    </div>
    <button class="btn-secondary" (click)="auth.logout()">Cerrar sesión</button>
  </div>

  @if (loading()) {
    <div class="loading-state">Consultando el registro académico...</div>
  } @else if (requests().length === 0) {
    <div class="empty-state">
      <h3>Sin registros</h3>
      <p>Aún no has generado solicitudes en el sistema de pañol.</p>
      <button class="btn-primary" style="margin-top: 1rem" (click)="back()">Ir al catálogo</button>
    </div>
  } @else {
    <div class="requests-grid">
      @for (req of requests(); track req.id) {
        <div class="card request-card">
          <div class="request-meta">
            <span class="request-id">REF: {{ req.id.slice(0, 8).toUpperCase() }}</span>
            <span class="badge" [ngClass]="'badge-' + req.estado.toLowerCase()">{{ req.estado }}</span>
          </div>
          
          <div class="request-date">Registrada el: {{ req.createdAt | date:'dd/MM/yyyy HH:mm' }}</div>
          
          <div class="request-items">
            @for (item of req.items; track item.recursoId) {
              <div class="item-chip">
                <span class="item-code">{{ resourceMap()[item.recursoId] || item.recursoId }}</span>
                <span class="item-qty">×{{ item.cantidad }}</span>
              </div>
            }
          </div>
          
          @if (req.estado === 'PENDIENTE') {
            <div class="request-actions">
              <button class="btn-secondary cancel-btn" (click)="cancel(req.id)">Anular Solicitud</button>
            </div>
          }
        </div>
      }
    </div>
  }
</div>
  `,
  styles: [`
    .page-layout { padding: 4rem 2rem; max-width: 1200px; margin: 0 auto; }
    .page-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 3rem; border-bottom: 2px solid var(--color-text); padding-bottom: 1.5rem; }
    .header-left { display: flex; flex-direction: column; gap: 1rem; align-items: flex-start; }
    .page-title { font-size: 3rem; margin: 0; }
    .back-btn { padding: 0.5rem 1rem; font-size: 0.85rem; border: none; background: transparent; padding-left: 0; }
    .back-btn:hover { background: transparent; color: var(--color-primary); }
    
    .loading-state, .empty-state { text-align: center; padding: 4rem; color: var(--color-text-muted); font-family: var(--font-display); font-style: italic; font-size: 1.25rem; }
    .empty-state h3 { font-size: 2rem; font-style: normal; margin-bottom: 0.5rem; color: var(--color-text); }
    
    .requests-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }
    
    .request-card { display: flex; flex-direction: column; gap: 1rem; border-top: 4px solid var(--color-text); }
    .request-card:hover { border-top-color: var(--color-primary); }
    
    .request-meta { display: flex; align-items: center; justify-content: space-between; }
    .request-id { font-family: monospace; font-size: 0.9rem; font-weight: 600; color: var(--color-text-muted); letter-spacing: 0.05em; }
    
    .request-date { font-size: 0.95rem; color: var(--color-text); border-bottom: 1px solid var(--color-border); padding-bottom: 1rem; }
    
    .request-items { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.5rem; flex: 1; }
    .item-chip { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px dashed var(--color-border); }
    .item-code { font-family: monospace; font-size: 0.9rem; color: var(--color-text-muted); }
    .item-qty { font-weight: 600; font-size: 0.9rem; }
    
    .request-actions { margin-top: 1.5rem; }
    .cancel-btn { width: 100%; border-color: var(--color-danger); color: var(--color-danger); }
    .cancel-btn:hover { background: #FEF2F2; color: #991B1B; border-color: #991B1B; }
  `],
  imports: [CommonModule],
})
export class MyRequestsComponent implements OnInit {
  private http = inject(HttpClient);
  protected auth = inject(AuthService);
  private router = inject(Router);

  requests = signal<any[]>([]);
  resourceMap = signal<Record<string, string>>({});
  loading = signal(true);

  async ngOnInit() {
    try {
      const [data, resources] = await Promise.all([
        firstValueFrom(this.http.get<any[]>('/api/requests')).catch(() => []),
        firstValueFrom(this.http.get<any[]>('/api/inventory/resources')).catch(() => [])
      ]);
      
      const map: Record<string, string> = {};
      resources.forEach(r => map[r.id] = r.nombre);
      this.resourceMap.set(map);
      this.requests.set(data);
    } finally {
      this.loading.set(false);
    }
  }

  async cancel(id: string) {
    await firstValueFrom(this.http.post(`/api/requests/${id}/cancel`, {})).catch(() => {});
    await this.ngOnInit();
  }

  back() { this.router.navigate(['/catalog']); }
}
