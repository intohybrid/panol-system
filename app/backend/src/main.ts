import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Habilitar CORS para que Angular pueda conectarse
  app.enableCors();
  
  // Habilitar validación automática
  app.useGlobalPipes(new ValidationPipe());

  const port = 3000;
  await app.listen(port, '0.0.0.0');
  console.log(`Backend de Panol System corriendo en: http://127.0.0.1:${port}/api`);
}
bootstrap();
