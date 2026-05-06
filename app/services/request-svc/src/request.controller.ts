import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { RequestService } from './request.service';

@Controller()
export class RequestController {
  constructor(private svc: RequestService) {}

  @Get('health')
  health() { return { status: 'ok', service: 'request-svc', port: 3003 }; }

  @Get('requests')
  findAll(@Query('userId') userId?: string) {
    return this.svc.findAll(userId);
  }

  @Get('requests/:id')
  findById(@Param('id') id: string) {
    return this.svc.findById(id);
  }

  @Post('requests')
  create(@Body() body: { userId: string; items: { recursoId: string; cantidad: number }[] }) {
    return this.svc.create(body.userId, body.items);
  }

  @Post('requests/:id/cancel')
  cancel(@Param('id') id: string) {
    return this.svc.cancel(id);
  }

  // Endpoint interno para que loan-svc actualice el estado
  @Post('requests/:id/status')
  updateStatus(@Param('id') id: string, @Body() body: { estado: any }) {
    return this.svc.updateStatus(id, body.estado);
  }
}
