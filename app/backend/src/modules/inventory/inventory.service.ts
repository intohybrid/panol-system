import { Injectable, NotFoundException } from '@nestjs/common';
import { InMemoryDb } from '../../shared/in-memory-db';
import { EventEmitter2, OnEvent } from '@nestjs/event-emitter';

@Injectable()
export class InventoryService {
  constructor(
    private db: InMemoryDb,
    private eventEmitter: EventEmitter2
  ) {}

  findAll() {
    return this.db.resources;
  }

  @OnEvent('request.created')
  handleRequestCreated(payload: any) {
    console.log('[Inventory] Reservando stock para solicitud:', payload.requestId);
    payload.items.forEach((item: any) => {
      const resource = this.db.resources.find(r => r.id === item.recursoId);
      if (resource) {
        resource.stockReservado += item.cantidad;
        console.log(`[Inventory] Recurso ${resource.nombre}: Reservado ${resource.stockReservado}/${resource.stock}`);
      }
    });
  }

  @OnEvent('loan.issued')
  handleLoanIssued(payload: any) {
    console.log('[Inventory] Confirmando salida de stock por préstamo:', payload.loanId);
    payload.items.forEach((item: any) => {
      const resource = this.db.resources.find(r => r.id === item.recursoId);
      if (resource) {
        resource.stock -= item.cantidad;
        resource.stockReservado -= item.cantidad;
        console.log(`[Inventory] Recurso ${resource.nombre}: Stock actual ${resource.stock}`);
      }
    });
  }
}
