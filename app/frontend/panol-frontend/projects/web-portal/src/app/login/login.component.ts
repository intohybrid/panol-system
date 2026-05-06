import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  documento = signal('');
  password = signal('');
  error = signal('');
  loading = signal(false);

  async onSubmit() {
    if (!this.documento() || !this.password()) return;
    this.error.set('');
    this.loading.set(true);
    try {
      await this.auth.login(this.documento(), this.password());
    } catch (e: any) {
      this.error.set(e?.error?.message || 'Credenciales inválidas');
    } finally {
      this.loading.set(false);
    }
  }

  // Helpers para demo rápido
  fillAlumno()       { this.documento.set('20123456-7'); this.password.set('alumno123'); }
  fillCoordinador()  { this.documento.set('12345678-9'); this.password.set('coordinador123'); }
  fillJefe()         { this.documento.set('13456789-0'); this.password.set('jefe123'); }
}
