import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AuthModule } from './auth.module';

async function bootstrap() {
  const app = await NestFactory.create(AuthModule);
  app.enableCors();
  app.useGlobalPipes(new ValidationPipe({ whitelist: true }));

  const port = 3001;
  await app.listen(port, '0.0.0.0');
  console.log(`[auth-svc] Corriendo en http://localhost:${port}`);
  console.log(`[auth-svc] 4 usuarios cargados (alumno, panolero, coordinador, jefe)`);
}
bootstrap();
