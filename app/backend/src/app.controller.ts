import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { InventoryService } from './modules/inventory/inventory.service';
import { RequestService } from './modules/request/request.service';
import { LoanService } from './modules/loan/loan.service';
import { AiService } from './modules/ai/ai.service';

@Controller('api')
export class AppController {
  constructor(
    private readonly inventory: InventoryService,
    private readonly request: RequestService,
    private readonly loan: LoanService,
    private readonly ai: AiService
  ) {}

  // --- IA Assistant ---
  @Post('ai/suggest')
  suggest(@Body() body: { prompt: string }) {
    return this.ai.suggestResources(body.prompt);
  }

  // --- Inventory ---
  @Get('inventory')
  getResources() {
    return this.inventory.findAll();
  }

  // --- Requests ---
  @Get('requests')
  getRequests() {
    return this.request.findAll();
  }

  @Post('requests')
  createRequest(@Body() body: { userId: string, items: any[] }) {
    return this.request.create(body.userId, body.items);
  }

  // --- Loans (Tótem) ---
  @Get('loans')
  getLoans() {
    return this.loan.findAll();
  }

  @Post('loans/:requestId/issue')
  issueLoan(@Param('requestId') requestId: string, @Body() body: { panoleroId: string }) {
    return this.loan.issueLoan(requestId, body.panoleroId);
  }

  @Post('loans/:loanId/return')
  returnLoan(@Param('loanId') loanId: string) {
    return this.loan.returnLoan(loanId);
  }
}
