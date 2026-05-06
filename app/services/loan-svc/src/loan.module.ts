import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { LoanController } from './loan.controller';
import { LoanService } from './loan.service';

@Module({
  imports: [HttpModule],
  controllers: [LoanController],
  providers: [LoanService],
})
export class LoanModule {}
