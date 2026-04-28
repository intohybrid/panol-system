import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from './services/api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent implements OnInit {
  api = inject(ApiService);
  userId = '1'; // Alumno Demo
  
  // Estado del chat con tipado explícito
  chatMessages = signal<{role: 'user' | 'ai', text: string}[]>([]);
  aiSuggestions = signal<any[]>([]);

  ngOnInit() {
    this.api.loadInventory();
  }

  async sendToAi(prompt: string) {
    if (!prompt.trim()) return;
    
    this.chatMessages.update((m: any[]) => [...m, { role: 'user', text: prompt }]);
    const response = await this.api.askAi(prompt);
    
    this.chatMessages.update((m: any[]) => [...m, { role: 'ai', text: response.message }]);
    this.aiSuggestions.set(response.suggestions);
  }

  async aceptarSugerencias() {
    const items = this.aiSuggestions();
    if (items.length > 0) {
      await this.api.createRequest(this.userId, items);
      alert('Solicitud creada mediante el Asistente IA');
      this.aiSuggestions.set([]);
      this.chatMessages.set([]);
    }
  }

  async solicitar(recursoId: string) {
    try {
      await this.api.createRequest(this.userId, [{ recursoId, cantidad: 1 }]);
      alert('Solicitud creada con éxito');
    } catch (e) {
      alert('Error al crear solicitud: ' + (e as any).error?.message);
    }
  }
}
