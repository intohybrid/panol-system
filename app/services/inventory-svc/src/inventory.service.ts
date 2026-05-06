import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import {
  Resource, ResourceWithStock, StockReservation,
  ReservationStatus, DEMO_TTL_MS
} from '../../../shared/src/index';

@Injectable()
export class InventoryService {
  // inventory_db in-memory
  private resources: Resource[] = [
    { id: 'res-1', nombre: 'Osciloscopio Digital', categoria: 'EQUIPO', stockTotal: 5, estado: 'ACTIVO', imagenUrl: 'https://placehold.co/200x150?text=Osciloscopio' },
    { id: 'res-2', nombre: 'Multímetro Fluke', categoria: 'EQUIPO', stockTotal: 10, estado: 'ACTIVO', imagenUrl: 'https://placehold.co/200x150?text=Multimetro' },
    { id: 'res-3', nombre: 'Kit Arduino Uno', categoria: 'MATERIAL', stockTotal: 20, estado: 'ACTIVO', imagenUrl: 'https://placehold.co/200x150?text=Arduino' },
    { id: 'res-4', nombre: 'Fuente de Alimentación DC', categoria: 'EQUIPO', stockTotal: 8, estado: 'ACTIVO', imagenUrl: 'https://placehold.co/200x150?text=Fuente+DC' },
    { id: 'res-5', nombre: 'Protoboard 830 puntos', categoria: 'MATERIAL', stockTotal: 30, estado: 'ACTIVO', imagenUrl: 'https://placehold.co/200x150?text=Protoboard' },
    { id: 'res-6', nombre: 'Pinza Amperimétrica', categoria: 'HERRAMIENTA', stockTotal: 6, estado: 'ACTIVO', imagenUrl: 'https://placehold.co/200x150?text=Pinza' },
  ];

  private reservations: StockReservation[] = [];

  findAll(): ResourceWithStock[] {
    return this.resources
      .filter(r => r.estado === 'ACTIVO')
      .map(r => ({ ...r, stockDisponible: this.calcDisponible(r.id) }));
  }

  findById(id: string): ResourceWithStock {
    const r = this.resources.find(r => r.id === id);
    if (!r) throw new NotFoundException(`Recurso ${id} no encontrado`);
    return { ...r, stockDisponible: this.calcDisponible(r.id) };
  }

  // Llamado por request-svc al crear solicitud
  reserve(requestId: string, items: { recursoId: string; cantidad: number }[]): void {
    // Validar disponibilidad de todos los ítems antes de reservar
    for (const item of items) {
      const disponible = this.calcDisponible(item.recursoId);
      if (disponible < item.cantidad) {
        const r = this.resources.find(r => r.id === item.recursoId);
        throw new BadRequestException(`Stock insuficiente para "${r?.nombre || item.recursoId}": disponible ${disponible}, solicitado ${item.cantidad}`);
      }
    }
    // Crear reservas
    const expiresAt = new Date(Date.now() + DEMO_TTL_MS);
    for (const item of items) {
      this.reservations.push({
        id: uuidv4(),
        requestId,
        recursoId: item.recursoId,
        cantidad: item.cantidad,
        status: 'ACTIVA',
        createdAt: new Date(),
        expiresAt,
      });
    }
  }

  // Llamado por loan-svc al materializar (descuenta stock definitivamente)
  consume(requestId: string): void {
    const reservas = this.reservations.filter(r => r.requestId === requestId && r.status === 'ACTIVA');
    for (const res of reservas) {
      const resource = this.resources.find(r => r.id === res.recursoId);
      if (resource) resource.stockTotal -= res.cantidad;
      res.status = 'CONSUMIDA';
    }
  }

  // Llamado al cancelar/vencer solicitud
  release(requestId: string): void {
    this.reservations
      .filter(r => r.requestId === requestId && r.status === 'ACTIVA')
      .forEach(r => (r.status = 'LIBERADA'));
  }

  // Llamado al devolver préstamo (restaura stock para ítems BUENO o DAÑADO)
  restore(items: { recursoId: string; cantidad: number }[]): void {
    for (const item of items) {
      const resource = this.resources.find(r => r.id === item.recursoId);
      if (resource) resource.stockTotal += item.cantidad;
    }
  }

  private calcDisponible(recursoId: string): number {
    const resource = this.resources.find(r => r.id === recursoId);
    if (!resource) return 0;
    const reservado = this.reservations
      .filter(r => r.recursoId === recursoId && r.status === 'ACTIVA')
      .reduce((sum, r) => sum + r.cantidad, 0);
    return resource.stockTotal - reservado;
  }
}
