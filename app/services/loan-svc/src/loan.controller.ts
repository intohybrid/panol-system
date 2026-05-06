import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { LoanService } from './loan.service';

@Controller()
export class LoanController {
  constructor(private svc: LoanService) {}

  @Get('health')
  health() { return { status: 'ok', service: 'loan-svc', port: 3004 }; }

  @Get('loans')
  findAll(@Query('userId') userId?: string) {
    return this.svc.findAll(userId);
  }

  @Get('loans/:id')
  findById(@Param('id') id: string) {
    return this.svc.findById(id);
  }

  @Post('loans/:requestId/materialize')
  materialize(
    @Param('requestId') requestId: string,
    @Body() body: { panoleroId: string },
  ) {
    return this.svc.materialize(requestId, body.panoleroId);
  }

  @Post('loans/:id/return')
  returnLoan(
    @Param('id') id: string,
    @Body() body: { items: { recursoId: string; cantidad: number; estado: any }[] },
  ) {
    return this.svc.returnLoan(id, body.items);
  }
}
