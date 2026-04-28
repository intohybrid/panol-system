import { Injectable, BadRequestException } from '@nestjs/common';
import { InMemoryDb } from '../../shared/in-memory-db';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class RequestService {
  constructor(
    private db: InMemoryDb,
    private eventEmitter: EventEmitter2
  ) {}

  create(userId: string, items: { recursoId: string, cantidad: number }[]) {
    // Validar disponibilidad
    for (const item of items) {
      const res = this.db.resources.find(r => r.id === item.recursoId);
      if (!res || (res.stock - res.stockReservado) < item.cantidad) {
        throw new BadRequestException(`Stock insuficiente para el recurso: ${res?.nombre || item.recursoId}`);
      }
    }

    const request = {
      id: uuidv4(),
      usuarioId: userId,
      items,
      estado: 'PENDIENTE',
      createdAt: new Date()
    };

    this.db.requests.push(request);
    
    // Emitir evento para que Inventory reserve el stock
    this.eventEmitter.emit('request.created', {
      requestId: request.id,
      items: request.items
    });

    return request;
  }

  findAll() {
    return this.db.requests;
  }
}
