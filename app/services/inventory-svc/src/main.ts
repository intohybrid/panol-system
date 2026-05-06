import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { InventoryModule } from './inventory.module';

async function bootstrap() {
  const app = await NestFactory.create(InventoryModule);
  app.enableCors();
  const port = 3002;
  await app.listen(port, '0.0.0.0');
  console.log(`[inventory-svc] Corriendo en http://localhost:${port}`);
}
bootstrap();
