import { Module } from '@nestjs/common';
import { EventEmitterModule } from '@nestjs/event-emitter';
import { InMemoryDb } from './shared/in-memory-db';
import { InventoryService } from './modules/inventory/inventory.service';
import { RequestService } from './modules/request/request.service';
import { LoanService } from './modules/loan/loan.service';
import { AiService } from './modules/ai/ai.service';
import { AppController } from './app.controller';

@Module({
  imports: [
    EventEmitterModule.forRoot()
  ],
  controllers: [AppController],
  providers: [
    InMemoryDb,
    InventoryService,
    RequestService,
    LoanService,
    AiService
  ],
})
export class AppModule {}
