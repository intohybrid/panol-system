import { Injectable } from '@nestjs/common';

@Injectable()
export class InMemoryDb {
  public users: any[] = [
    { id: '1', rut: '12345678-9', nombre: 'Alumno Demo', role: 'ALUMNO', pin: '1234' },
    { id: '2', rut: '98765432-1', nombre: 'Pañolero Demo', role: 'PANOLERO', pin: '0000' }
  ];

  public resources: any[] = [
    { id: 'res-1', nombre: 'Osciloscopio Digital', categoria: 'EQUIPO', stock: 5, stockReservado: 0 },
    { id: 'res-2', nombre: 'Multímetro Fluke', categoria: 'EQUIPO', stock: 10, stockReservado: 0 },
    { id: 'res-3', nombre: 'Kit Arduino Uno', categoria: 'MATERIAL', stock: 20, stockReservado: 0 }
  ];

  public requests: any[] = [];
  public loans: any[] = [];
}
