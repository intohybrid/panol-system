import * as bcrypt from 'bcrypt';
import { User } from '../../../shared/src/index';

const SALT = 10;

// Demo seed — 4 usuarios, uno por rol relevante para el flujo principal
// Contraseñas hasheadas con bcrypt (salt=10) según ARQUITECTURA-DEMO.md §2
export const DEMO_USERS: User[] = [
  {
    id: 'user-alumno-1',
    documento: '20123456-7',
    nombre: 'María González',
    role: 'ALUMNO',
    status: 'ACTIVO',
    passwordHash: bcrypt.hashSync('alumno123', SALT),
    pinHash: null,
  },
  {
    id: 'user-panolero-1',
    documento: '11234567-8',
    nombre: 'Esteban Solís',
    role: 'PANOLERO',
    status: 'ACTIVO',
    passwordHash: bcrypt.hashSync('panolero123', SALT),
    pinHash: bcrypt.hashSync('1234', SALT),
  },
  {
    id: 'user-coordinador-1',
    documento: '12345678-9',
    nombre: 'Carmen Vidal',
    role: 'COORDINADOR',
    status: 'ACTIVO',
    passwordHash: bcrypt.hashSync('coordinador123', SALT),
    pinHash: null,
  },
  {
    id: 'user-jefe-1',
    documento: '13456789-0',
    nombre: 'Roberto Fuentes',
    role: 'JEFE',
    status: 'ACTIVO',
    passwordHash: bcrypt.hashSync('jefe123', SALT),
    pinHash: null,
  },
];
