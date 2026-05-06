export type RequestStatus =
  | 'PENDIENTE'
  | 'MATERIALIZADA'
  | 'MATERIALIZADA_PARCIAL'
  | 'VENCIDA'
  | 'CANCELADA';

export type RequestType = 'NORMAL' | 'ESPECIAL';

export interface RequestItem {
  recursoId: string;
  cantidad: number;
}

export interface Request {
  id: string;
  usuarioId: string;
  items: RequestItem[];
  estado: RequestStatus;
  tipo: RequestType;
  ttlExpiresAt: Date;
  createdAt: Date;
  updatedAt: Date;
}
