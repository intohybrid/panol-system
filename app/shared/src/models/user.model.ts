export type UserRole = 'ALUMNO' | 'DOCENTE' | 'PANOLERO' | 'COORDINADOR' | 'JEFE';
export type UserStatus = 'ACTIVO' | 'INACTIVO' | 'BLOQUEADO';

export interface User {
  id: string;
  documento: string;
  nombre: string;
  role: UserRole;
  status: UserStatus;
  passwordHash: string;
  pinHash: string | null;
}

export interface UserPublic {
  id: string;
  documento: string;
  nombre: string;
  role: UserRole;
  status: UserStatus;
}
