import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { RequestModule } from './request.module';

async function bootstrap() {
  const app = await NestFactory.create(RequestModule);
  app.enableCors();
  const port = 3003;
  await app.listen(port, '0.0.0.0');
  console.log(`[request-svc] Corriendo en http://localhost:${port}`);
}
bootstrap();
