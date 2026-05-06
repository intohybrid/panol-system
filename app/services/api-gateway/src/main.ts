import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { GatewayModule } from './gateway.module';

async function bootstrap() {
  const app = await NestFactory.create(GatewayModule);
  app.setGlobalPrefix('api');

  // CORS explícito — permite los dos frontends Angular (ARQUITECTURA-DEMO.md §4)
  app.enableCors({
    origin: ['http://localhost:4200', 'http://localhost:4201'],
    methods: ['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  });

  const port = 3000;
  await app.listen(port, '0.0.0.0');
  console.log(`[api-gateway] Corriendo en http://localhost:${port}`);
  console.log(`[api-gateway] Portal:  http://localhost:4200  -> /api`);
  console.log(`[api-gateway] Tótem:   http://localhost:4201  -> /api`);
}
bootstrap();
