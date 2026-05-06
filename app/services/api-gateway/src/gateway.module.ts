import { Module, MiddlewareConsumer, NestModule } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { HttpModule } from '@nestjs/axios';
import { GatewayController } from './gateway.controller';
import { JwtMiddleware } from './middleware/jwt.middleware';
import { JWT_SECRET } from '../../../shared/src/index';

@Module({
  imports: [
    HttpModule,
    JwtModule.register({ secret: JWT_SECRET }),
  ],
  controllers: [GatewayController],
})
export class GatewayModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(JwtMiddleware).forRoutes('*');
  }
}
