import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { AiModule } from './ai.module';

async function bootstrap() {
  const app = await NestFactory.create(AiModule);
  app.enableCors();
  const port = 3005;
  await app.listen(port, '0.0.0.0');
  console.log(`[ai-assistant-svc] Corriendo en http://localhost:${port}`);
}
bootstrap();
