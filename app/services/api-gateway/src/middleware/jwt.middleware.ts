import { Injectable, NestMiddleware, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { Request, Response, NextFunction } from 'express';

// Rutas que no requieren JWT
const PUBLIC_ROUTES = [
  { method: 'POST', path: '/api/auth/login' },
  { method: 'POST', path: '/api/auth/login-pin' },
  { method: 'GET', path: '/api/health' },
];

@Injectable()
export class JwtMiddleware implements NestMiddleware {
  constructor(private jwtService: JwtService) {}

  use(req: Request, res: Response, next: NextFunction) {
    if (req.method === 'OPTIONS') return next();

    console.log(`[JwtMiddleware] Validating ${req.method} ${req.path} (originalUrl: ${req.originalUrl})`);

    const isPublic = PUBLIC_ROUTES.some(
      r => r.method === req.method && req.originalUrl.startsWith(r.path),
    );

    if (isPublic) {
      console.log(`[JwtMiddleware] Route is public, skipping JWT check`);
      return next();
    }

    const auth = req.headers['authorization'];
    if (!auth?.startsWith('Bearer ')) {
      throw new UnauthorizedException('Token requerido');
    }

    try {
      const payload = this.jwtService.verify(auth.split(' ')[1]);
      (req as any).user = payload;
      next();
    } catch {
      throw new UnauthorizedException('Token inválido o expirado');
    }
  }
}
