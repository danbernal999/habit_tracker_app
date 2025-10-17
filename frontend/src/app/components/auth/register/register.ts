import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../services/auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
})
export class Register {
  username: string = '';
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  errorMessage: string = '';
  successMessage: string = '';
  loading: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onRegister(): void {
    // Validaciones
    if (!this.username || !this.email || !this.password || !this.confirmPassword) {
      this.errorMessage = "Por favor, complete todos los campos.";
      return;
    }

    if (this.password !== this.confirmPassword) {
      this.errorMessage = "Las contraseñas no coinciden.";
      return;
    }

    if (this.password.length < 8) {
      this.errorMessage = "La contraseña debe tener al menos 8 caracteres.";
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.authService.register(this.username, this.email, this.password).subscribe({
      next: (response) => {
        console.log('Registro exitoso:', response);
        this.successMessage = '¡Cuenta creada exitosamente! Redirigiendo al login...';
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
        console.error('Error de registro:', error);
        if (error.error?.detail) {
          this.errorMessage = error.error.detail;
        } else {
          this.errorMessage = 'Error al registrar. Intente de nuevo.';
        }
        this.loading = false;
      },
      complete: () => {
        this.loading = false;
      }
    });
  }
}
