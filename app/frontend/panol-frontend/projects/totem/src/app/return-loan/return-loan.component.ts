import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../services/api.service';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-return-loan',
  standalone: true,
  templateUrl: './return-loan.component.html',
  styleUrl: './return-loan.component.css',
})
export class ReturnLoanComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  protected api = inject(ApiService);
  private auth = inject(AuthService);

  loanId = signal<string>('');
  loan = signal<any>(null);
  
  // Estado de los items devueltos
  itemStatuses = signal<Record<string, string>>({});
  
  showPinModal = signal(false);
  confirmPin = signal('');
  pinError = signal('');

  async ngOnInit() {
    this.loanId.set(this.route.snapshot.paramMap.get('id') || '');
    if (!this.loanId()) {
      this.cancel();
      return;
    }
    
    // Asegurar que tenemos los préstamos cargados
    if (this.api.loans().length === 0) {
      await this.api.loadLoans();
    }
    
    // Buscar la request original para ver qué items tiene
    const activeLoan = this.api.loans().find(l => l.id === this.loanId());
    if (!activeLoan) {
      this.cancel();
      return;
    }
    
    if (this.api.requests().length === 0) {
      await this.api.loadRequests();
    }
    
    const request = this.api.requests().find(r => r.id === activeLoan.requestId);
    this.loan.set({
      ...activeLoan,
      items: request?.items || []
    });
    
    // Inicializar todos en BUENO por defecto
    const statuses: Record<string, string> = {};
    for (const item of this.loan().items) {
      statuses[item.recursoId] = 'BUENO';
    }
    this.itemStatuses.set(statuses);
  }

  setStatus(recursoId: string, status: string) {
    this.itemStatuses.update(st => ({ ...st, [recursoId]: status }));
  }

  requestConfirm() {
    this.showPinModal.set(true);
    this.confirmPin.set('');
    this.pinError.set('');
  }

  appendDigit(digit: number) {
    if (this.confirmPin().length < 4) {
      this.confirmPin.update(p => p + digit);
    }
  }

  deleteDigit() {
    this.confirmPin.update(p => p.slice(0, -1));
  }

  cancelModal() {
    this.showPinModal.set(false);
  }

  async submitReturn() {
    if (this.confirmPin().length !== 4) return;
    
    this.pinError.set('');
    
    // Verificar PIN
    const isValid = await this.auth.verifyPin(this.confirmPin());
    if (!isValid) {
      this.pinError.set('PIN incorrecto. Intente nuevamente.');
      this.confirmPin.set('');
      return;
    }
    
    // Formatear items para el API
    const items = this.loan().items.map((i: any) => ({
      recursoId: i.recursoId,
      cantidad: i.cantidad,
      estado: this.itemStatuses()[i.recursoId]
    }));
    
    try {
      await this.api.returnLoan(this.loanId(), items);
      this.router.navigate(['/dashboard']);
    } catch (e: any) {
      this.pinError.set(e?.error?.message || 'Error al procesar devolución');
    }
  }

  cancel() {
    this.router.navigate(['/dashboard']);
  }
}
