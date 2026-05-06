import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { SERVICE_URLS } from '../../../shared/src/index';

@Injectable()
export class AiService {
  constructor(private http: HttpService) {}

  async processMessage(prompt: string, userId: string) {
    // Obtener inventario disponible para buscar coincidencias
    let resources: any[] = [];
    try {
      const res = await firstValueFrom(this.http.get(`${SERVICE_URLS.INVENTORY}/resources`));
      resources = res.data;
    } catch { resources = []; }

    const p = prompt.toLowerCase();
    const suggestions = resources.filter(r => {
      const n = r.nombre.toLowerCase();
      return (
        p.includes(n.split(' ')[0]) ||
        p.includes(r.categoria.toLowerCase()) ||
        (p.includes('medir') && n.includes('osciloscopio')) ||
        (p.includes('voltaje') && (n.includes('multímetro') || n.includes('multimetro'))) ||
        (p.includes('alimentar') && n.includes('fuente')) ||
        (p.includes('circuito') && (n.includes('protoboard') || n.includes('arduino')))
      );
    });

    const message = suggestions.length > 0
      ? `Encontré ${suggestions.length} recurso(s) que podrían servirte. ¿Los agrego a tu solicitud?`
      : 'No encontré recursos específicos. Prueba con "necesito medir voltaje", "circuito", "osciloscopio", etc.';

    return {
      message,
      suggestions: suggestions.map(s => ({
        recursoId: s.id,
        nombre: s.nombre,
        cantidad: 1,
        stockDisponible: s.stockDisponible,
      })),
    };
  }
}
