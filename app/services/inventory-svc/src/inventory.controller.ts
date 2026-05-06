import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { InventoryService } from './inventory.service';

@Controller()
export class InventoryController {
  constructor(private svc: InventoryService) {}

  @Get('health')
  health() { return { status: 'ok', service: 'inventory-svc', port: 3002 }; }

  @Get('resources')
  findAll() { return this.svc.findAll(); }

  @Get('resources/:id')
  findById(@Param('id') id: string) { return this.svc.findById(id); }

  // Endpoints internos llamados por otros servicios (simula eventos AMQP)
  @Post('stock/reserve')
  reserve(@Body() body: { requestId: string; items: { recursoId: string; cantidad: number }[] }) {
    this.svc.reserve(body.requestId, body.items);
    return { ok: true };
  }

  @Post('stock/consume')
  consume(@Body() body: { requestId: string }) {
    this.svc.consume(body.requestId);
    return { ok: true };
  }

  @Post('stock/release')
  release(@Body() body: { requestId: string }) {
    this.svc.release(body.requestId);
    return { ok: true };
  }

  @Post('stock/restore')
  restore(@Body() body: { items: { recursoId: string; cantidad: number }[] }) {
    this.svc.restore(body.items);
    return { ok: true };
  }
}
