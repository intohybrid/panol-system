import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from './services/api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent implements OnInit {
  api = inject(ApiService);
  panoleroId = '2'; // Pañolero Demo
  view = signal<'solicitudes' | 'prestamos'>('solicitudes');

  ngOnInit() {
    this.api.loadRequests();
    this.api.loadLoans();
  }

  async materializar(requestId: string) {
    const pin = prompt('Ingrese su PIN de Pañolero para autorizar (Demo: 0000):');
    if (pin === '0000') {
      try {
        await this.api.issueLoan(requestId, this.panoleroId);
        alert('Préstamo materializado con éxito. Se ha generado el ticket digital.');
      } catch (e) {
        alert('Error: ' + (e as any).error?.message);
      }
    } else {
      alert('PIN Incorrecto.');
    }
  }

  async devolver(loanId: string) {
    try {
      await this.api.returnLoan(loanId);
      alert('Devolución registrada correctamente.');
    } catch (e) {
      alert('Error en devolución.');
    }
  }
}
