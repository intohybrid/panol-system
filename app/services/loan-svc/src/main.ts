import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { LoanModule } from './loan.module';

async function bootstrap() {
  const app = await NestFactory.create(LoanModule);
  app.enableCors();
  const port = 3004;
  await app.listen(port, '0.0.0.0');
  console.log(`[loan-svc] Corriendo en http://localhost:${port}`);
}
bootstrap();
