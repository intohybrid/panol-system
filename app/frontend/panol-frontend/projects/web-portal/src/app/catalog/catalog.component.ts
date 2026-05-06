import { Component, inject, signal, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../auth/auth.service';

interface Resource {
  id: string;
  nombre: string;
  categoria: string;
  stockTotal: number;
  stockDisponible: number;
  estado: string;
  imagenUrl?: string;
}

@Component({
  selector: 'app-catalog',
  standalone: true,
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.css',
})
export class CatalogComponent implements OnInit {
  private http = inject(HttpClient);
  protected auth = inject(AuthService);
  private router = inject(Router);

  resources = signal<Resource[]>([]);
  loading = signal(true);
  error = signal('');
  chatMessages = signal<{ role: 'user' | 'assistant'; text: string }[]>([
    { role: 'assistant', text: '¡Hola! Cuéntame qué necesitas hacer y te ayudo a armar tu solicitud.' },
  ]);
  aiSuggestions = signal<any[]>([]);
  selectedItems = signal<{ recursoId: string; nombre: string; cantidad: number }[]>([]);
  requestSuccess = signal<string | null>(null);

  async ngOnInit() {
    await this.loadInventory();
  }

  async loadInventory() {
    this.loading.set(true);
    try {
      const data = await firstValueFrom(this.http.get<Resource[]>('/api/inventory/resources'));
      this.resources.set(data);
    } catch {
      this.error.set('Error cargando inventario. ¿El backend está corriendo?');
    } finally {
      this.loading.set(false);
    }
  }

  async sendToAi(input: HTMLInputElement) {
    const prompt = input.value.trim();
    if (!prompt) return;
    this.chatMessages.update(m => [...m, { role: 'user', text: prompt }]);
    input.value = '';
    try {
      const res: any = await firstValueFrom(
        this.http.post('/api/assistant/messages', { prompt }),
      );
      this.chatMessages.update(m => [...m, { role: 'assistant', text: res.message }]);
      if (res.suggestions?.length > 0) this.aiSuggestions.set(res.suggestions);
    } catch {
      this.chatMessages.update(m => [...m, { role: 'assistant', text: 'Error consultando el asistente.' }]);
    }
  }

  addItem(resource: Resource) {
    this.selectedItems.update(items => {
      const existing = items.find(i => i.recursoId === resource.id);
      if (existing) return items;
      return [...items, { recursoId: resource.id, nombre: resource.nombre, cantidad: 1 }];
    });
  }

  removeItem(recursoId: string) {
    this.selectedItems.update(items => items.filter(i => i.recursoId !== recursoId));
  }

  async acceptSuggestions() {
    const suggestions = this.aiSuggestions();
    this.selectedItems.update(items => {
      const extra = suggestions.filter(s => !items.find(i => i.recursoId === s.recursoId));
      return [...items, ...extra.map(s => ({ recursoId: s.recursoId, nombre: s.nombre, cantidad: 1 }))];
    });
    this.aiSuggestions.set([]);
    this.chatMessages.update(m => [...m, { role: 'assistant', text: `Agregué ${suggestions.length} recurso(s) a tu carrito.` }]);
  }

  async createRequest() {
    const items = this.selectedItems().map(i => ({ recursoId: i.recursoId, cantidad: i.cantidad }));
    if (!items.length) return;
    try {
      await firstValueFrom(this.http.post('/api/requests', { items }));
      this.requestSuccess.set(`Solicitud creada exitosamente. Recógela en el pañol.`);
      this.selectedItems.set([]);
      await this.loadInventory();
      setTimeout(() => this.requestSuccess.set(null), 5000);
    } catch (e: any) {
      this.error.set(e?.error?.message || 'Error al crear la solicitud');
      setTimeout(() => this.error.set(''), 4000);
    }
  }

  logout() { this.auth.logout(); }
  goToMyRequests() { this.router.navigate(['/my-requests']); }
}
