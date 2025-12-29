import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { AssessmentsService, AssessmentItem } from '../../../services/assessments.service';

@Component({
  selector: 'app-complete-assessments',
  imports: [Header, Footer, CommonModule, FormsModule],
  templateUrl: './complete-assessments.html',
  standalone: true,
})
export default class CompleteAssessments {
  loading = true;
  errorMessage = '';
  searchTerm = '';

  allAssessments: AssessmentItem[] = [];
  filteredAssessments: AssessmentItem[] = [];
  selectedAssessment: AssessmentItem | null = null;

  constructor(private assessmentsService: AssessmentsService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    console.log('[CompleteAssessments] ngOnInit called');
    this.fetchAssessments();
  }

  private fetchAssessments(): void {
    this.loading = true;
    this.errorMessage = '';
    console.log('[CompleteAssessments] Fetching assessments...');
    this.assessmentsService.getAll().subscribe({
      next: (res) => {
        console.log('[CompleteAssessments] Received data:', res);
        console.log('[CompleteAssessments] Number of items:', res.items?.length);
        this.allAssessments = res.items || [];
        console.log(
          '[CompleteAssessments] allAssessments set to:',
          this.allAssessments.length,
          'items'
        );
        this.filteredAssessments = [...this.allAssessments];
        console.log(
          '[CompleteAssessments] filteredAssessments set to:',
          this.filteredAssessments.length,
          'items'
        );
        if (this.filteredAssessments.length > 0) {
          console.log(
            '[CompleteAssessments] Selecting first assessment:',
            this.filteredAssessments[0]
          );
          this.selectAssessment(this.filteredAssessments[0]);
        }
        this.loading = false;
        this.cdr.markForCheck();
        this.cdr.detectChanges();
        console.log('[CompleteAssessments] Loading set to false, data should now display');
      },
      error: (err: any) => {
        console.error('[CompleteAssessments] Error:', err);
        this.errorMessage = err?.message || 'Erro a carregar avaliações.';
        this.loading = false;
      },
    });
  }

  onSearchChange(): void {
    const term = this.searchTerm.toLowerCase().trim();
    console.log(
      '[CompleteAssessments] onSearchChange called, searchTerm:',
      this.searchTerm,
      'lowercase term:',
      term
    );

    let newFiltered: AssessmentItem[] = [];
    if (!term) {
      newFiltered = [...this.allAssessments];
      console.log('[CompleteAssessments] Empty search term, showing all:', newFiltered.length);
    } else {
      const beforeCount = this.allAssessments.length;
      newFiltered = this.allAssessments.filter(
        (a) =>
          (a.employee_name?.toLowerCase() || '').includes(term) ||
          a.id.toString().includes(term) ||
          (a.risk_level?.toLowerCase() || '').includes(term)
      );
      console.log('[CompleteAssessments] Search term:', term);
      console.log(
        '[CompleteAssessments] Before:',
        beforeCount,
        'After filter:',
        newFiltered.length
      );
      console.log('[CompleteAssessments] First 3 results:', newFiltered.slice(0, 3));
    }

    // Force a new array reference for Angular to detect changes
    this.filteredAssessments = [...newFiltered];
    console.log(
      '[CompleteAssessments] filteredAssessments updated to:',
      this.filteredAssessments.length
    );

    // Auto-select first result if current selection is filtered out
    if (
      this.selectedAssessment &&
      !this.filteredAssessments.find((a) => a.id === this.selectedAssessment?.id)
    ) {
      if (this.filteredAssessments.length > 0) {
        this.selectAssessment(this.filteredAssessments[0]);
      } else {
        this.selectedAssessment = null;
      }
    }
    // Trigger change detection to update the filtered list display
    this.cdr.markForCheck();
    this.cdr.detectChanges();
    console.log('[CompleteAssessments] detectChanges called');
  }

  trackByAssessmentId(index: number, assessment: AssessmentItem): number {
    return assessment.id;
  }

  formatDimensionName(key: string): string {
    const names: { [key: string]: string } = {
      stress: 'Stress',
      ansiedade: 'Ansiedade',
      depressao: 'Depressão',
      burnout: 'Burnout',
      sono: 'Sono',
      turnos: 'Turnos',
      ergonomia: 'Ergonomia',
      geral: 'Geral',
    };
    return names[key] || key;
  }

  getDimensionTooltip(key: string): string {
    const tooltips: { [key: string]: string } = {
      stress: 'Nível de stress: 0% = sem stress | 100% = máximo stress',
      ansiedade: 'Nível de ansiedade: 0% = sem ansiedade | 100% = máxima ansiedade',
      depressao: 'Indicadores de depressão: 0% = nenhum | 100% = máximo',
      burnout: 'Síndrome de burnout: 0% = nenhum risco | 100% = risco máximo',
      sono: 'Qualidade do sono: 0% = muito bom | 100% = muito comprometido',
      turnos: 'Impacto dos turnos de trabalho: 0% = sem impacto | 100% = impacto máximo',
      ergonomia: 'Problemas ergonómicos: 0% = nenhum | 100% = máximo',
      geral: 'Bem-estar geral: 0% = excelente | 100% = crítico',
    };
    return tooltips[key] || 'Percentagem de risco nesta dimensão';
  }

  selectAssessment(assessment: AssessmentItem): void {
    this.selectedAssessment = assessment;
    console.log('[CompleteAssessments] Selected assessment:', assessment);
    console.log('[CompleteAssessments] per_dimension data:', assessment.per_dimension);
    console.log(
      '[CompleteAssessments] per_dimension keys:',
      Object.keys(assessment.per_dimension || {})
    );
  }

  getDimensionKeys(): string[] {
    if (!this.selectedAssessment?.per_dimension) return [];
    return Object.keys(this.selectedAssessment.per_dimension);
  }

  getDimensionScore(key: string): number {
    const dimensionData = this.selectedAssessment?.per_dimension[key];
    if (!dimensionData) return 0;
    // dimensionData can be {score, max, percent} or just a number
    if (typeof dimensionData === 'object' && 'percent' in dimensionData) {
      return dimensionData.percent;
    }
    const num = Number(dimensionData);
    return isNaN(num) ? 0 : num;
  }

  getRiskColor(riskLevel: string): string {
    const lower = riskLevel.toLowerCase();
    if (lower.includes('baixo') || lower.includes('1')) return 'bg-green-100 text-green-800';
    if (lower.includes('moderado') || lower.includes('2') || lower.includes('3'))
      return 'bg-yellow-100 text-yellow-800';
    if (lower.includes('alto') || lower.includes('4') || lower.includes('5'))
      return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  }
}
