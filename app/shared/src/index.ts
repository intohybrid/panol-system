export * from './models/user.model';
export * from './models/resource.model';
export * from './models/request.model';
export * from './models/loan.model';

// Nombres canónicos de eventos de dominio (alineados con 03-eventos-dominio.md)
export const DomainEvents = {
  REQUEST_CREATED: 'request.created',
  REQUEST_CANCELLED: 'request.cancelled',
  REQUEST_EXPIRED: 'request.expired',
  REQUEST_MATERIALIZED: 'request.materialized',
  LOAN_ISSUED: 'loan.issued',
  LOAN_RETURNED: 'loan.returned',
  STOCK_RESERVED: 'stock.reserved',
  STOCK_RELEASED: 'stock.released',
  STOCK_CONSUMED: 'stock.consumed',
  STOCK_RESTORED: 'stock.restored',
} as const;

// URL base de cada servicio (usados por api-gateway y por servicios que se llaman entre sí)
export const SERVICE_URLS = {
  AUTH: 'http://127.0.0.1:3001',
  INVENTORY: 'http://127.0.0.1:3002',
  REQUEST: 'http://127.0.0.1:3003',
  LOAN: 'http://127.0.0.1:3004',
  AI_ASSISTANT: 'http://127.0.0.1:3005',
} as const;

export const DEMO_TTL_MS = 30 * 60 * 1000; // 30 minutos
export const JWT_SECRET = 'PANOL_DEMO_SECRET_2026';
export const JWT_EXPIRES_IN = '8h';
