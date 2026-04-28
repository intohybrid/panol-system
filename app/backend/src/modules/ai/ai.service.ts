import { Injectable } from '@nestjs/common';
import { InMemoryDb } from '../../shared/in-memory-db';

@Injectable()
export class AiService {
  constructor(private db: InMemoryDb) {}

  async suggestResources(prompt: string) {
    console.log('[AI] Procesando prompt:', prompt);
    
    // Simulación de procesamiento de lenguaje natural
    // En un entorno real, aquí llamaríamos a OpenAI/Claude pasándole el inventario
    const suggestions = this.db.resources.filter(res => {
      const p = prompt.toLowerCase();
      const n = res.nombre.toLowerCase();
      // Búsqueda simple por palabras clave
      return p.includes(n.split(' ')[0].toLowerCase()) || 
             p.includes(res.categoria.toLowerCase()) ||
             (p.includes('medir') && res.nombre.includes('Osciloscopio')) ||
             (p.includes('voltaje') && res.nombre.includes('Multímetro'));
    });

    return {
      message: suggestions.length > 0 
        ? `He encontrado ${suggestions.length} recursos que podrían servirte. ¿Quieres que los agregue a tu solicitud?`
        : "No estoy seguro de qué recursos necesitas. ¿Podrías ser más específico? Pruebe con 'necesito medir voltaje' o 'osciloscopio'.",
      suggestions: suggestions.map(s => ({ recursoId: s.id, nombre: s.nombre, cantidad: 1 }))
    };
  }
}
