# Panol System — Guía de Desarrollo Frontend (Angular)

Este documento detalla las instrucciones y estándares para construir las interfaces de usuario del sistema utilizando **Angular 19+**. Aplicamos las mejores prácticas modernas centradas en señales (Signals), componentes standalone y una arquitectura orientada a dominios.

## 1. Stack Tecnológico Frontend

- **Framework**: Angular 19 (Standalone Components).
- **Reactividad**: Angular Signals (`signal`, `computed`, `resource`).
- **Estilos**: Vanilla CSS + CSS Variables (según mandato de diseño).
- **Estado**: Signals + Servicios de Estado locales.
- **Iconos**: Lucide Angular o SVG inline.
- **Testing**: Vitest + Angular Testing Library.

---

## 2. Estructura de Aplicaciones

Dividiremos el frontend en dos aplicaciones principales dentro del monorepo (usando Angular Workspaces o Nx si se prefiere):

### A. Portal Web (`apps/web-portal`)
Orientado a Alumnos y Docentes.
- **Vistas**: Home, Catálogo, Mis Solicitudes, Perfil.
- **IA**: Chatbot flotante integrado con `ai-assistant-svc`.

### B. Tótem de Atención (`apps/totem`)
Orientado a Pañoleros.
- **Vistas**: Dashboard Diario, Validación de Solicitud, Gestión de Préstamos, Devoluciones.
- **Seguridad**: Teclado numérico virtual para ingreso de PIN.

---

## 3. Estándares de Implementación (Basado en Angular Skills)

### 3.1. Reactividad con Signals
Evitamos `RxJS` para el estado simple, prefiriendo Signals:
```typescript
// Ejemplo de servicio de catálogo
@Injectable({ providedIn: 'root' })
export class CatalogService {
  private http = inject(HttpClient);
  
  // Recurso asíncrono usando la nueva API resource (v19)
  resources = resource({
    loader: () => firstValueFrom(this.http.get<Resource[]>('/api/inventory/resources'))
  });
}
```

### 3.2. Componentes Standalone y Control Flow
Usamos la sintaxis moderna para plantillas:
```html
@if (resources.isLoading()) {
  <app-skeleton />
} @else {
  @for (item of resources.value(); track item.id) {
    <app-resource-card [data]="item" />
  } @empty {
    <p>No hay recursos disponibles.</p>
  }
}
```

### 3.3. Inyección de Dependencias
Preferimos la función `inject()` sobre el constructor para mayor claridad y soporte de tipos:
```typescript
export class RequestComponent {
  private requestService = inject(RequestService);
  private router = inject(Router);
  
  user = input.required<User>(); // Signal-based input
}
```

---

## 4. Integración con el Backend (Gateway)

Todas las llamadas se dirigen al `API Gateway` (Puerto 3000 en el demo).

| Funcionalidad | Método | Endpoint |
|---|---|---|
| Login | `POST` | `/auth/login` |
| Lista Recursos | `GET` | `/inventory/resources` |
| Crear Solicitud | `POST` | `/requests` |
| Validar Solicitud | `GET` | `/requests/:id` |
| Materializar Préstamo | `POST` | `/loans/:id/issue` |

---

## 5. Hoja de Ruta del Frontend

1. [ ] Configurar el Workspace de Angular.
2. [ ] Implementar el `AuthInterceptor` para adjuntar el JWT a las peticiones.
3. [ ] Crear la librería de componentes compartidos (`ui-kit`): Botones, Inputs, Cards (usando Vanilla CSS).
4. [ ] Implementar el Shell del Portal Web con el asistente IA.
5. [ ] Implementar el Shell del Tótem con el flujo de validación.

---

## 6. Comandos Útiles

```bash
# Crear componente standalone
ng generate component components/resource-card --standalone

# Ejecutar tests
ng test

# Build para producción
ng build --configuration production
```
