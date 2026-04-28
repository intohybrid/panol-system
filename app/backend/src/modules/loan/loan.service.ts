import { Injectable, NotFoundException } from '@nestjs/common';
import { InMemoryDb } from '../../shared/in-memory-db';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class LoanService {
  constructor(
    private db: InMemoryDb,
    private eventEmitter: EventEmitter2
  ) {}

  issueLoan(requestId: string, panoleroId: string) {
    const request = this.db.requests.find(r => r.id === requestId);
    if (!request) throw new NotFoundException('Solicitud no encontrada');
    if (request.estado !== 'PENDIENTE') throw new Error('La solicitud ya no está pendiente');

    const loan = {
      id: uuidv4(),
      requestId: request.id,
      usuarioId: request.usuarioId,
      panoleroId: panoleroId,
      items: request.items,
      estado: 'ACTIVO',
      issuedAt: new Date()
    };

    request.estado = 'MATERIALIZADO';
    this.db.loans.push(loan);

    // Emitir evento para que Inventory descuente el stock definitivamente
    this.eventEmitter.emit('loan.issued', {
      loanId: loan.id,
      items: loan.items
    });

    return loan;
  }

  returnLoan(loanId: string) {
    const loan = this.db.loans.find(l => l.id === loanId);
    if (!loan) throw new NotFoundException('Préstamo no encontrado');
    
    loan.estado = 'DEVUELTO';
    loan.returnedAt = new Date();

    // Emitir evento para que Inventory reabra el stock (esto es una simplificación)
    this.eventEmitter.emit('loan.returned', {
      loanId: loan.id,
      items: loan.items
    });

    return loan;
  }

  findAll() {
    return this.db.loans;
  }
}
