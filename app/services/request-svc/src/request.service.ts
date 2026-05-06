import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { v4 as uuidv4 } from 'uuid';
import { Request, RequestStatus, RequestItem, DEMO_TTL_MS, SERVICE_URLS } from '../../../shared/src/index';

@Injectable()
export class RequestService {
  // request_db in-memory
  private requests: Request[] = [];

  constructor(private http: HttpService) {}

  async create(userId: string, items: RequestItem[]): Promise<Request> {
    // 1. Reservar stock en inventory-svc (simula: request-svc → inventory.reserve)
    await firstValueFrom(
      this.http.post(`${SERVICE_URLS.INVENTORY}/stock/reserve`, { requestId: 'temp', items }),
    ).catch(err => {
      const msg = err?.response?.data?.message || 'Stock insuficiente';
      throw new BadRequestException(msg);
    });

    const request: Request = {
      id: uuidv4(),
      usuarioId: userId,
      items,
      estado: 'PENDIENTE',
      tipo: 'NORMAL',
      ttlExpiresAt: new Date(Date.now() + DEMO_TTL_MS),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    // 2. Re-llamar con el ID real
    await firstValueFrom(
      this.http.post(`${SERVICE_URLS.INVENTORY}/stock/release`, { requestId: 'temp' }),
    ).catch(() => {});
    await firstValueFrom(
      this.http.post(`${SERVICE_URLS.INVENTORY}/stock/reserve`, { requestId: request.id, items }),
    );

    this.requests.push(request);

    // 3. TTL: expirar automáticamente (simula message expiration)
    setTimeout(async () => {
      const r = this.requests.find(r => r.id === request.id);
      if (r && r.estado === 'PENDIENTE') {
        r.estado = 'VENCIDA';
        r.updatedAt = new Date();
        await firstValueFrom(
          this.http.post(`${SERVICE_URLS.INVENTORY}/stock/release`, { requestId: request.id }),
        ).catch(() => {});
        console.log(`[request-svc] Solicitud ${request.id} expiró (TTL)`);
      }
    }, DEMO_TTL_MS);

    return request;
  }

  findAll(userId?: string): Request[] {
    if (userId) return this.requests.filter(r => r.usuarioId === userId);
    return this.requests;
  }

  findById(id: string): Request {
    const r = this.requests.find(r => r.id === id);
    if (!r) throw new NotFoundException(`Solicitud ${id} no encontrada`);
    return r;
  }

  async cancel(id: string): Promise<Request> {
    const r = this.findById(id);
    if (r.estado !== 'PENDIENTE') throw new BadRequestException('Solo se pueden cancelar solicitudes PENDIENTE');
    r.estado = 'CANCELADA';
    r.updatedAt = new Date();
    await firstValueFrom(
      this.http.post(`${SERVICE_URLS.INVENTORY}/stock/release`, { requestId: id }),
    ).catch(() => {});
    return r;
  }

  // Llamado internamente por loan-svc al materializar
  updateStatus(id: string, estado: RequestStatus): Request {
    const r = this.findById(id);
    r.estado = estado;
    r.updatedAt = new Date();
    return r;
  }
}
