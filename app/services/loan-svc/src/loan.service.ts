import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { v4 as uuidv4 } from 'uuid';
import { Loan, LoanItem, ReturnItemStatus, SERVICE_URLS } from '../../../shared/src/index';

@Injectable()
export class LoanService {
  // loan_db in-memory
  private loans: Loan[] = [];

  constructor(private http: HttpService) {}

  async materialize(requestId: string, panoleroId: string): Promise<Loan> {
    // 1. Obtener y validar la solicitud en request-svc
    let request: any;
    try {
      const res = await firstValueFrom(this.http.get(`${SERVICE_URLS.REQUEST}/requests/${requestId}`));
      request = res.data;
    } catch {
      throw new NotFoundException(`Solicitud ${requestId} no encontrada`);
    }

    if (request.estado !== 'PENDIENTE') {
      throw new BadRequestException(`Solicitud en estado "${request.estado}", no se puede materializar`);
    }
    if (new Date(request.ttlExpiresAt) < new Date()) {
      throw new BadRequestException('La solicitud ha expirado (TTL vencido)');
    }

    // 2. Consumir stock en inventory-svc
    await firstValueFrom(
      this.http.post(`${SERVICE_URLS.INVENTORY}/stock/consume`, { requestId }),
    );

    // 3. Actualizar estado de la solicitud en request-svc
    await firstValueFrom(
      this.http.post(`${SERVICE_URLS.REQUEST}/requests/${requestId}/status`, { estado: 'MATERIALIZADA' }),
    );

    // 4. Crear préstamo
    const loan: Loan = {
      id: uuidv4(),
      ticketId: `TICK-${Date.now()}`,
      requestId,
      usuarioId: request.usuarioId,
      panoleroId,
      items: request.items.map((item: any) => ({
        recursoId: item.recursoId,
        cantidad: item.cantidad,
        estadoDevolucion: null,
      })),
      estado: 'ACTIVO',
      fechaLimite: new Date(Date.now() + 4 * 60 * 60 * 1000), // 4h para demo
      issuedAt: new Date(),
      returnedAt: null,
    };

    this.loans.push(loan);
    console.log(`[loan-svc] Préstamo ${loan.id} creado para solicitud ${requestId}`);
    return loan;
  }

  async returnLoan(
    id: string,
    returnItems: { recursoId: string; cantidad: number; estado: ReturnItemStatus }[],
  ): Promise<Loan> {
    const loan = this.loans.find(l => l.id === id);
    if (!loan) throw new NotFoundException(`Préstamo ${id} no encontrado`);
    if (loan.estado !== 'ACTIVO') throw new BadRequestException('El préstamo ya fue cerrado');

    // Actualizar estado por ítem
    for (const ret of returnItems) {
      const item = loan.items.find(i => i.recursoId === ret.recursoId);
      if (item) item.estadoDevolucion = ret.estado;
    }

    // Restaurar stock solo para ítems BUENO o DAÑADO (no FALTANTE)
    const itemsARestaurar = returnItems
      .filter(i => i.estado === 'BUENO' || i.estado === 'DAÑADO')
      .map(i => ({ recursoId: i.recursoId, cantidad: i.cantidad }));

    if (itemsARestaurar.length > 0) {
      await firstValueFrom(
        this.http.post(`${SERVICE_URLS.INVENTORY}/stock/restore`, { items: itemsARestaurar }),
      );
    }

    loan.estado = 'DEVUELTO';
    loan.returnedAt = new Date();
    return loan;
  }

  findAll(userId?: string): Loan[] {
    if (userId) return this.loans.filter(l => l.usuarioId === userId);
    return this.loans;
  }

  findById(id: string): Loan {
    const l = this.loans.find(l => l.id === id);
    if (!l) throw new NotFoundException(`Préstamo ${id} no encontrado`);
    return l;
  }
}
