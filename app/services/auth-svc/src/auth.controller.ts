import { Controller, Post, Get, Body, Headers, UnauthorizedException, Param } from '@nestjs/common';
import { AuthService } from './auth.service';
import { JwtService } from '@nestjs/jwt';

@Controller()
export class AuthController {
  constructor(
    private authService: AuthService,
    private jwtService: JwtService,
  ) {}

  @Get('health')
  health() {
    return { status: 'ok', service: 'auth-svc', port: 3001 };
  }

  // Login con documento + contraseña (Portal web)
  @Post('auth/login')
  login(@Body() body: { documento: string; password: string }) {
    return this.authService.login(body.documento, body.password);
  }

  // Login por PIN (Tótem — ARQUITECTURA-DEMO.md §7)
  @Post('auth/login-pin')
  loginByPin(@Body() body: { pin: string }) {
    return this.authService.loginByPin(body.pin);
  }

  // Reconfirmación de PIN para acciones sensibles (ya autenticado)
  @Post('auth/verify-pin')
  verifyPin(
    @Body() body: { pin: string },
    @Headers('authorization') auth: string,
  ) {
    const payload = this.decodeToken(auth);
    return this.authService.verifyPin(payload.sub, body.pin);
  }

  // Perfil del usuario autenticado
  @Get('auth/me')
  getMe(@Headers('authorization') auth: string) {
    const payload = this.decodeToken(auth);
    return this.authService.getUserById(payload.sub);
  }

  // Resolución de nombres por IDs (usado por tótem para mostrar nombres)
  @Get('auth/users/:id')
  getUserById(@Param('id') id: string) {
    return this.authService.getUserById(id);
  }

  @Post('auth/users/batch')
  getUsersByIds(@Body() body: { ids: string[] }) {
    return this.authService.getUsersByIds(body.ids);
  }

  private decodeToken(auth: string) {
    if (!auth?.startsWith('Bearer ')) throw new UnauthorizedException('Token requerido');
    try {
      return this.jwtService.verify(auth.split(' ')[1]);
    } catch {
      throw new UnauthorizedException('Token inválido');
    }
  }
}
