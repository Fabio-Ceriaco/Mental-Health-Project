import { LoginService } from './../../services/login.service';
import { Component, EventEmitter, Input, Output, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RegisterService } from '../../services/register.service';

@Component({
  selector: 'app-register-modal',
  imports: [FormsModule],
  templateUrl: './register-modal.html',
  styleUrl: './register-modal.css',
})
export class RegisterModal {
  @Output() closed = new EventEmitter<void>();
  @Input() consentGiven!: boolean;
  form: any = {
    employee_id: '',
    email: '',
    password: '',
    confirmPassword: '',
  };
  registerError: string = '';
  registerSuccess: string = '';
  showModal: boolean = true;
  saving: boolean = false;
  rgpdOpened: boolean = false;

  constructor(
    private registerService: RegisterService,
    private loginService: LoginService,
    private cdr: ChangeDetectorRef
  ) {}

  submit() {
    this.registerError = '';
    this.registerSuccess = '';
    this.cdr.detectChanges();

    if (!this.consentGiven) {
      this.registerError = 'Você deve aceitar os termos de consentimento.';
      this.cdr.detectChanges();
      return;
    }

    // Basic validation
    if (this.form.password !== this.form.confirmPassword) {
      this.registerError = 'As senhas não coincidem.';
      this.cdr.detectChanges();
      return;
    } else if (this.form.password.length < 8) {
      this.registerError = 'A senha deve ter pelo menos 8 caracteres.';
      this.cdr.detectChanges();
      return;
    } else if (!/\d/.test(this.form.password)) {
      this.registerError = 'A senha deve conter pelo menos um número.';
      this.cdr.detectChanges();
      return;
    } else if (!/[!@#$%^&*]/.test(this.form.password)) {
      this.registerError = 'A senha deve conter pelo menos um caractere especial (!@#$%^&*).';
      this.cdr.detectChanges();
      return;
    } else if (!/[A-Z]/.test(this.form.password)) {
      this.registerError = 'A senha deve conter pelo menos uma letra maiúscula.';
      this.cdr.detectChanges();
      return;
    }

    const userData = {
      email: this.form.email,
      password: this.form.password,
    };
    this.saving = true;
    this.cdr.detectChanges();
    console.log('Registering user:', userData); // Debug log
    this.registerService.register(userData).subscribe({
      next: (res: any) => {
        this.registerError = '';
        this.registerSuccess = 'Registro bem-sucedido! Você já pode fazer login.';
        this.saving = false;
        this.cdr.detectChanges();
        // Optionally, auto-login after registration
        // this.loginService.login(this.form.email, this.form.password).subscribe({
        //   next: (res: any) => {
        //     this.loginService.salvarToken(res.access_token);
        //     this.loginService.salvarUser(res.utilizador);
        //     this.loginService.salvarEmployee(res.employee);
        //     window.location.reload();
        //   },

        // },);
        this.closed.emit();
      },
      error: (err: any) => {
        this.registerSuccess = '';
        this.saving = false;

        // Extract error message from various possible response formats
        let errorMessage = 'Erro no registro. Por favor, tente novamente.';

        if (err?.error?.detail) {
          errorMessage = err.error.detail;
        } else if (err?.error?.message) {
          errorMessage = err.error.message;
        } else if (err?.error?.error) {
          errorMessage = err.error.error;
        } else if (typeof err?.error === 'string') {
          errorMessage = err.error;
        } else if (err?.message) {
          errorMessage = err.message;
        }

        this.registerError = errorMessage;
        this.cdr.detectChanges();
        console.error('Registration error:', err); // Debug log
      },
    });
  }
  close() {
    this.closed.emit();
  }
}
