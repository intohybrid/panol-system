export type LoanStatus = 'ACTIVO' | 'DEVUELTO' | 'ANULADO';
export type ReturnItemStatus = 'BUENO' | 'DAÑADO' | 'FALTANTE';

export interface LoanItem {
  recursoId: string;
  cantidad: number;
  estadoDevolucion: ReturnItemStatus | null; // null mientras está activo
}

export interface Loan {
  id: string;
  ticketId: string;
  requestId: string;
  usuarioId: string;
  panoleroId: string;
  items: LoanItem[];
  estado: LoanStatus;
  fechaLimite: Date;
  issuedAt: Date;
  returnedAt: Date | null;
}
