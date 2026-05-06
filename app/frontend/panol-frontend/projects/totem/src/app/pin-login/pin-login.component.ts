import { Component, inject, signal } from '@angular/core';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-pin-login',
  standalone: true,
  templateUrl: './pin-login.component.html',
  styleUrl: './pin-login.component.css',
})
export class PinLoginComponent {
  private auth = inject(AuthService);

  pin = signal('');
  error = signal('');
  loading = signal(false);

  appendDigit(digit: number) {
    if (this.pin().length < 4) {
      this.pin.update(p => p + digit);
    }
  }

  deleteDigit() {
    this.pin.update(p => p.slice(0, -1));
  }

  async submit() {
    if (this.pin().length !== 4) return;
    this.error.set('');
    this.loading.set(true);
    try {
      await this.auth.loginByPin(this.pin());
    } catch (e: any) {
      this.error.set(e?.error?.message || 'PIN incorrecto');
      this.pin.set('');
    } finally {
      this.loading.set(false);
    }
  }
}
