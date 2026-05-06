import { Injectable, UnauthorizedException, NotFoundException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { DEMO_USERS } from './seed/users.seed';
import { User, UserPublic } from '../../../shared/src/index';

@Injectable()
export class AuthService {
  // Colección in-memory (simula auth_db en demo)
  private users: User[] = [...DEMO_USERS];

  constructor(private jwtService: JwtService) {}

  async login(documento: string, password: string): Promise<{ accessToken: string; user: UserPublic }> {
    const user = this.users.find(u => u.documento === documento);
    if (!user) throw new UnauthorizedException('Credenciales inválidas');
    if (user.status === 'BLOQUEADO') throw new UnauthorizedException('Usuario bloqueado');

    const valid = await bcrypt.compare(password, user.passwordHash);
    if (!valid) throw new UnauthorizedException('Credenciales inválidas');

    const token = this.signToken(user);
    return { accessToken: token, user: this.toPublic(user) };
  }

  // Autenticación por PIN para el tótem (ARQUITECTURA-DEMO.md §7)
  async loginByPin(pin: string): Promise<{ accessToken: string; user: UserPublic }> {
    // Busca el pañolero cuyo PIN coincida
    for (const user of this.users) {
      if (user.role !== 'PANOLERO' || !user.pinHash) continue;
      const valid = await bcrypt.compare(pin, user.pinHash);
      if (valid) {
        const token = this.signToken(user);
        return { accessToken: token, user: this.toPublic(user) };
      }
    }
    throw new UnauthorizedException('PIN incorrecto');
  }

  // Reconfirmación de PIN para acciones sensibles (ya autenticado)
  async verifyPin(userId: string, pin: string): Promise<{ ok: boolean }> {
    const user = this.users.find(u => u.id === userId);
    if (!user || !user.pinHash) throw new UnauthorizedException('Usuario no tiene PIN configurado');

    const valid = await bcrypt.compare(pin, user.pinHash);
    if (!valid) throw new UnauthorizedException('PIN incorrecto');
    return { ok: true };
  }

  getUserById(id: string): UserPublic {
    const user = this.users.find(u => u.id === id);
    if (!user) throw new NotFoundException(`Usuario ${id} no encontrado`);
    return this.toPublic(user);
  }

  getUsersByIds(ids: string[]): UserPublic[] {
    return ids.map(id => {
      const u = this.users.find(u => u.id === id);
      return u ? this.toPublic(u) : null;
    }).filter(Boolean) as UserPublic[];
  }

  private signToken(user: User): string {
    const payload = {
      sub: user.id,
      role: user.role,
      nombre: user.nombre,
      documento: user.documento,
    };
    return this.jwtService.sign(payload);
  }

  private toPublic(user: User): UserPublic {
    return {
      id: user.id,
      documento: user.documento,
      nombre: user.nombre,
      role: user.role,
      status: user.status,
    };
  }
}
