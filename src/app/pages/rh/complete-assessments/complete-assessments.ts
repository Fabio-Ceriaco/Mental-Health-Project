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
    this.fetchAssessments();
  }

  private fetchAssessments(): void {
    this.loading = true;
    this.errorMessage = '';

    this.assessmentsService.getAll().subscribe({
      next: (res) => {
        this.allAssessments = res.items || [];
        this.filteredAssessments = [...this.allAssessments];

        if (this.filteredAssessments.length > 0) {
          this.selectAssessment(this.filteredAssessments[0]);
        }

        this.loading = false;
        this.cdr.markForCheck();
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.errorMessage = err?.message || 'Erro a carregar avaliações.';
        this.loading = false;
      },
    });
  }

  onSearchChange(): void {
    const term = this.searchTerm.toLowerCase().trim();

    let newFiltered: AssessmentItem[] = [];
    if (!term) {
      newFiltered = [...this.allAssessments];
    } else {
      newFiltered = this.allAssessments.filter(
        (a) =>
          (a.employee_name?.toLowerCase() || '').includes(term) ||
          a.id.toString().includes(term) ||
          (a.risk_level?.toLowerCase() || '').includes(term)
      );
    }

    // Force a new array reference for Angular to detect changes
    this.filteredAssessments = [...newFiltered];

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
      carga_trabalho: 'Carga Trabalho',
      equilibrio_vida: 'Equilíbrio Vida',
      reconhecimento: 'Reconhecimento',
      suporte_social: 'Suporte Social',
      lideranca: 'Liderança',
      seguranca_psicologica: 'Seg. Psicológica',
      seguranca_emprego: 'Seg. Emprego',
      autonomia: 'Autonomia',
      proposito: 'Propósito',
      regulacao_emocional: 'Reg. Emocional',
      sintomas_fisicos: 'Sint. Físicos',
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
      carga_trabalho: 'Carga de trabalho: 0% = adequada | 100% = excessiva',
      equilibrio_vida: 'Equilíbrio vida-trabalho: 0% = excelente | 100% = muito comprometido',
      reconhecimento:
        'Reconhecimento e valorização: 0% = muito valorizado | 100% = não reconhecido',
      suporte_social: 'Suporte social no trabalho: 0% = excelente | 100% = muito isolado',
      lideranca: 'Qualidade da liderança: 0% = excelente | 100% = muito deficiente',
      seguranca_psicologica:
        'Segurança psicológica: 0% = total segurança | 100% = medo e insegurança',
      seguranca_emprego: 'Segurança no emprego: 0% = estável | 100% = muito inseguro',
      autonomia: 'Autonomia no trabalho: 0% = total autonomia | 100% = sem controlo',
      proposito: 'Propósito e significado: 0% = muito significativo | 100% = sem propósito',
      regulacao_emocional: 'Regulação emocional: 0% = estável | 100% = muito instável',
      sintomas_fisicos: 'Sintomas físicos: 0% = nenhum | 100% = sintomas graves',
      geral: 'Bem-estar geral: 0% = excelente | 100% = crítico',
    };
    return tooltips[key] || 'Percentagem de risco nesta dimensão';
  }

  selectAssessment(assessment: AssessmentItem): void {
    this.selectedAssessment = assessment;
    console.log('Selected assessment:', assessment);
    console.log('Per dimension keys:', Object.keys(assessment.per_dimension || {}));
    console.log('Per dimension data:', assessment.per_dimension);
  }

  getDimensionKeys(): string[] {
    // If no assessment selected, return empty
    if (!this.selectedAssessment?.per_dimension) return [];

    // Return the actual dimensions that exist in the data
    return Object.keys(this.selectedAssessment.per_dimension);
  }

  getDimensionScore(key: string): number {
    if (!this.selectedAssessment?.per_dimension) return 0;

    const dimensionData = this.selectedAssessment.per_dimension[key];
    if (!dimensionData) {
      console.log(`No data for dimension: ${key}`);
      return 0;
    }

    // dimensionData structure: {score: number, max: number, percent: number}
    if (typeof dimensionData === 'object' && 'percent' in dimensionData) {
      return dimensionData.percent;
    }

    // Fallback if it's just a number
    const num = Number(dimensionData);
    return isNaN(num) ? 0 : num;
  }

  getDimensionColor(key: string): string {
    // Use consistent gray tones for all dimensions
    return 'text-gray-700';
  }

  getDimensionBorderColor(key: string): string {
    // Use consistent border for all dimensions
    return 'border-gray-300';
  }

  getDimensionBgColor(key: string): string {
    // Use consistent background for all dimensions
    return 'bg-white';
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
