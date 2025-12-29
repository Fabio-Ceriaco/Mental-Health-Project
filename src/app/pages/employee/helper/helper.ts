import { Component } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Router } from '@angular/router';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
@Component({
  selector: 'app-helper',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, Header, Footer],
  templateUrl: './helper.html',
  styleUrls: ['./helper.css'],
})
export default class Helper {
  supportOptions = [
    'Psicologia',
    'Coaching',
    'Formação em Gestão de stress',
    'Assédio Sexual',
    'Assédio Moral',
  ];
  selectedServices: string[] = [];
  subject = '';
  message = '';
  successMessage = '';
  errorMessage = '';
  submitting = false;

  constructor(private location: Location, private router: Router) {}

  goBack() {
    this.router.navigate(['/employee-dashboard']);
  }

  toggleService(option: string, checked: boolean) {
    if (checked) {
      if (!this.selectedServices.includes(option)) this.selectedServices.push(option);
    } else {
      this.selectedServices = this.selectedServices.filter((s) => s !== option);
    }
  }

  submitHelp() {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.subject.trim() || !this.message.trim()) {
      this.errorMessage = 'Preencha o assunto e a mensagem.';
      return;
    }

    if (!this.selectedServices.length) {
      this.errorMessage = 'Selecione pelo menos um tipo de apoio.';
      return;
    }

    this.submitting = true;

    // Submit help request

    // Placeholder for API call
    setTimeout(() => {
      this.successMessage = 'Pedido submetido com sucesso. Obrigado!';
      this.selectedServices = [];
      this.subject = '';
      this.message = '';
      this.submitting = false;
    }, 400);
  }
}
