import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AssessmentService } from '../../../services/assessment.service';
import { LoginService } from '../../../services/login.service';
import { Footer } from '../../../components/footer/footer';
import { Header } from '../../../components/header/header';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-new-evaluation',
  standalone: true,
  imports: [CommonModule, FormsModule, Footer, Header],
  templateUrl: './new-evaluation.html',
  styleUrls: ['./new-evaluation.css'],
})
export default class NewEvaluation implements OnInit {
  //loading = true;
  saving = false;
  successMessage: string = '';
  errorMessage: string = '';

  //questions: any[] = [];
  pages: any[][] = [];
  pageIndex = 0;

  answers: Record<number, number> = {};
  //assessmentId = 1; // Hardcoded for now

  employeeId?: number;

  //------------  Constructor ------------//
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private loginService: LoginService,
    private assessment: AssessmentService
  ) {}

  //------------  Lifecycle Hooks------------//
  ngOnInit(): void {
    this.employeeId = this.loginService.employee_Id()!; // Non-null assertion
    const questions = this.route.snapshot.data['questions'] ?? []; // Get resolved questions

    this.pages = this.splitIntoPages(questions, 5); // 5 questions per page
  }

  //------------ Pagination Methods ------------//
  splitIntoPages(list: any[], size: number): any[][] {
    const pages = [];
    for (let i = 0; i < list.length; i += size) {
      // Increment by page size
      pages.push(list.slice(i, i + size)); // Slice the list to get the page
    }

    return pages;
  }
  //------------ Navigation Methods ------------//
  nextPage() {
    if (this.pageIndex < this.pages.length - 1) this.pageIndex++; // Move to next page
  }

  prevPage() {
    if (this.pageIndex > 0) this.pageIndex--; // Move to previous page
  }

  goBack() {
    this.router.navigate(['/employee/dashboard']);
  }
  //------------ Evaluation Methods ------------//
  isPageComplete(): boolean {
    return this.pages[this.pageIndex].every((q) => this.answers[q.id] != undefined); // Check if all questions on the page are answered
  }
  //------------ Submission Method ------------//
  submit() {
    if (!this.pages.every((page) => page.every((q) => this.answers[q.id] != undefined))) {
      // Check if all questions are answered
      this.errorMessage = 'Por favor, responda todas as perguntas antes de enviar.';
      setTimeout(() => (this.errorMessage = ''), 5000); // Clear message after 5 seconds
      return;
    }
    this.saving = true;
    this.errorMessage = '';
    this.successMessage = '';

    const payload = {
      employee_id: this.employeeId,
      assessment_id: 1, // Hardcoded for now
      responses: Object.keys(this.answers).map((key) => ({
        // Convert keys to numbers
        question_id: Number(key), // Ensure question_id is a number
        answer_value: this.answers[Number(key)], // Ensure answer_value is a number
      })),
    };

    this.assessment.submitAnswers(payload).subscribe({
      next: () => {
        this.saving = false;
        this.successMessage = 'Avaliação enviada com sucesso! Redirecionando...';
        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
          this.router.navigate(['/employee/dashboard']);
        }, 2000);
      },
      error: (error) => {
        this.saving = false;
        this.errorMessage = 'Erro ao enviar avaliação. Tente novamente mais tarde.';
        console.error('Error submitting assessment:', error);
        setTimeout(() => (this.errorMessage = ''), 5000); // Clear message after 5 seconds
      },
    });
  }
}
