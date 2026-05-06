export type ResourceCategory = 'EQUIPO' | 'MATERIAL' | 'HERRAMIENTA';
export type ResourceStatus = 'ACTIVO' | 'EN_MANTENCION' | 'BAJA';
export type ReservationStatus = 'ACTIVA' | 'CONSUMIDA' | 'LIBERADA';

export interface Resource {
  id: string;
  nombre: string;
  categoria: ResourceCategory;
  stockTotal: number;
  estado: ResourceStatus;
  imagenUrl?: string;
}

export interface ResourceWithStock extends Resource {
  stockDisponible: number; // stockTotal - sum(reservas ACTIVAS)
}

export interface StockReservation {
  id: string;
  requestId: string;
  recursoId: string;
  cantidad: number;
  status: ReservationStatus;
  createdAt: Date;
  expiresAt: Date;
}
