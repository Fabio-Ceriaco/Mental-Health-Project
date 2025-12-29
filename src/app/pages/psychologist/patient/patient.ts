import { ChangeDetectionStrategy, ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { AssessmentsService, AssessmentItem } from '../../../services/assessments.service';
import { InterventionsService } from '../../../services/interventions.service';
import { finalize, timeout } from 'rxjs/operators';

@Component({
  selector: 'app-patient',
  imports: [CommonModule, FormsModule, Header, Footer],
  templateUrl: './patient.html',
  styleUrls: ['./patient.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export default class Patient {
  // Static options
  estadoOptions: string[] = ['Ativo', 'Em acompanhamento', 'Alta'];

  // Patient selector
  patientsOptions: Array<{ id: number; name: string }> = [];
  selectedPatientId: number | null = null;
  filteredPatients: Array<{ id: number; name: string }> = [];
  patientSearch = '';
  routePatientId: number | null = null;

  // Patient identity
  userName = '';
  userId: number | null = null;

  // Consultations derived from assessments
  consultasOptions: Array<{ data: string; assessment: AssessmentItem }> = [];
  selectedAssessment: AssessmentItem | null = null;

  loading = true;
  errorMessage = '';
  interventionMessage = '';
  interventionError = '';
  savingIntervention = false;
  recommendationText = '';

  private allAssessments: AssessmentItem[] = [];

  constructor(
    private assessmentsService: AssessmentsService,
    private interventionsService: InterventionsService,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const qp = this.route.snapshot.queryParamMap.get('patientId');
    const pid = qp ? Number(qp) : null;
    this.routePatientId = pid && !isNaN(pid) ? pid : null;
    this.fetchAssessments();
  }

  private fetchAssessments(): void {
    this.loading = true;
    this.errorMessage = '';
    this.assessmentsService
      .getAll()
      .pipe(
        timeout(10000),
        finalize(() => {
          this.loading = false;
          this.cdr.markForCheck();
        })
      )
      .subscribe({
        next: (res) => {
          this.allAssessments = res.items || [];

          // Build patient options
          const byId = new Map<number, string>();
          for (const i of this.allAssessments) {
            if (i.employee_id != null && !byId.has(i.employee_id)) {
              byId.set(i.employee_id, i.employee_name || `Colab ${i.employee_id}`);
            }
          }
          this.patientsOptions = Array.from(byId.entries())
            .map(([id, name]) => ({ id, name }))
            .sort((a, b) => a.name.localeCompare(b.name));

          this.applyPatientSearchFilter();

          if (
            this.routePatientId &&
            this.patientsOptions.some((p) => p.id === this.routePatientId)
          ) {
            this.selectedPatientId = this.routePatientId;
          } else if (this.patientsOptions.length > 0 && this.selectedPatientId == null) {
            this.selectedPatientId = this.patientsOptions[0].id;
          }

          this.syncPatientState();
        },
        error: (err: any) => {
          this.errorMessage = err?.message || 'Erro a carregar avaliações.';
        },
      });
  }

  onPatientChange(event: Event): void {
    const sel = event.target as HTMLSelectElement;
    const id = Number(sel.value);
    this.selectedPatientId = isNaN(id) ? null : id;
    this.syncPatientState();
  }

  onPatientSearchChange(): void {
    this.applyPatientSearchFilter();
  }

  onConsultaChange(event: Event): void {
    const sel = event.target as HTMLSelectElement;
    const date = sel.value;
    const found = this.consultasOptions.find((c) => c.data === date);
    this.selectedAssessment = found?.assessment || null;
  }

  private syncPatientState(): void {
    if (!this.selectedPatientId || this.allAssessments.length === 0) {
      this.userName = '';
      this.userId = null;
      this.consultasOptions = [];
      this.selectedAssessment = null;
      return;
    }

    const patientItems = this.allAssessments.filter(
      (i) => i.employee_id === this.selectedPatientId
    );
    if (patientItems.length === 0) {
      this.userName = '';
      this.userId = this.selectedPatientId;
      this.consultasOptions = [];
      this.selectedAssessment = null;
      return;
    }

    // Identity from first item
    const first = patientItems[0];
    this.userName = first.employee_name || `Colab ${first.employee_id}`;
    this.userId = first.employee_id;

    // Build consultations sorted by date desc
    this.consultasOptions = patientItems
      .sort((a, b) => (a.created_at < b.created_at ? 1 : -1))
      .map((i) => ({ data: i.created_at, assessment: i }));

    // Preselect latest
    this.selectedAssessment = this.consultasOptions[0]?.assessment || null;
  }

  // Dimension helpers (neutral styling, always show 18 keys)
  formatDimensionName(key: string): string {
    const names: { [key: string]: string } = {
      stress: 'Stress',
      ansiedade: 'Ansiedade',
      anxiety: 'Ansiedade',
      depressao: 'Depressão',
      depression: 'Depressão',
      burnout: 'Burnout',
      sono: 'Sono',
      sleep: 'Sono',
      turnos: 'Turnos',
      shifts: 'Turnos',
      ergonomia: 'Ergonomia',
      ergonomics: 'Ergonomia',
      carga_trabalho: 'Carga Trabalho',
      workload: 'Carga Trabalho',
      equilibrio_vida: 'Equilíbrio Vida',
      work_life_balance: 'Equilíbrio Vida',
      reconhecimento: 'Reconhecimento',
      recognition: 'Reconhecimento',
      suporte_social: 'Suporte Social',
      social_support: 'Suporte Social',
      lideranca: 'Liderança',
      leadership: 'Liderança',
      seguranca_psicologica: 'Seg. Psicológica',
      psychological_safety: 'Seg. Psicológica',
      seguranca_emprego: 'Seg. Emprego',
      job_security: 'Seg. Emprego',
      autonomia: 'Autonomia',
      autonomy: 'Autonomia',
      proposito: 'Propósito',
      purpose: 'Propósito',
      regulacao_emocional: 'Reg. Emocional',
      emotional_regulation: 'Reg. Emocional',
      sintomas_fisicos: 'Sint. Físicos',
      physical_symptoms: 'Sint. Físicos',
    };
    return names[key] || key;
  }

  getDimensionKeys(): string[] {
    if (!this.selectedAssessment?.per_dimension) return [];

    // Show every dimension present in the data
    const availableDimensions = Object.keys(this.selectedAssessment.per_dimension);

    // Sort them in a consistent order
    const order = [
      'stress',
      'ansiedade',
      'depressao',
      'burnout',
      'sono',
      'turnos',
      'ergonomia',
      'carga_trabalho',
      'equilibrio_vida',
      'reconhecimento',
      'suporte_social',
      'lideranca',
      'seguranca_psicologica',
      'seguranca_emprego',
      'autonomia',
      'proposito',
      'regulacao_emocional',
      'sintomas_fisicos',
    ];

    return availableDimensions.sort((a, b) => {
      const indexA = order.indexOf(a);
      const indexB = order.indexOf(b);
      return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
    });
  }

  getDimensionPercent(key: string): number {
    const d = this.selectedAssessment?.per_dimension?.[key];
    if (!d) return 0;
    const p = typeof d === 'object' && 'percent' in d ? d.percent : Number(d);
    return isNaN(Number(p)) ? 0 : Number(p);
  }

  private applyPatientSearchFilter(): void {
    const term = this.patientSearch.toLowerCase().trim();
    this.filteredPatients = term
      ? this.patientsOptions.filter(
          (p) => p.name.toLowerCase().includes(term) || p.id.toString().includes(term)
        )
      : [...this.patientsOptions];
    // Keep selection valid
    if (
      this.selectedPatientId &&
      !this.filteredPatients.find((p) => p.id === this.selectedPatientId)
    ) {
      this.selectedPatientId = this.filteredPatients[0]?.id ?? null;
    }
  }

  getDimensionTooltip(key: string): string {
    const tooltips: { [key: string]: string } = {
      stress: 'Nível de stress: 0% = sem stress | 100% = máximo stress',
      ansiedade: 'Nível de ansiedade: 0% = sem ansiedade | 100% = máxima ansiedade',
      depressao: 'Indicadores de depressão: 0% = nenhum | 100% = máximo',
      burnout: 'Síndrome de burnout: 0% = nenhum risco | 100% = risco máximo',
      sono: 'Qualidade do sono: 0% = muito bom | 100% = muito comprometido',
      turnos: 'Impacto dos turnos: 0% = sem impacto | 100% = impacto máximo',
      ergonomia: 'Problemas ergonómicos: 0% = nenhum | 100% = máximo',
      carga_trabalho: 'Carga de trabalho: 0% = adequada | 100% = excessiva',
      equilibrio_vida: 'Equilíbrio vida-trabalho: 0% = excelente | 100% = comprometido',
      reconhecimento: 'Reconhecimento: 0% = muito valorizado | 100% = não reconhecido',
      suporte_social: 'Suporte social: 0% = excelente | 100% = muito isolado',
      lideranca: 'Liderança: 0% = excelente | 100% = muito deficiente',
      seguranca_psicologica:
        'Segurança psicológica: 0% = segurança total | 100% = medo/insegurança',
      seguranca_emprego: 'Segurança no emprego: 0% = estável | 100% = muito inseguro',
      autonomia: 'Autonomia: 0% = total autonomia | 100% = sem controlo',
      proposito: 'Propósito: 0% = muito significativo | 100% = sem propósito',
      regulacao_emocional: 'Regulação emocional: 0% = estável | 100% = instável',
      sintomas_fisicos: 'Sintomas físicos: 0% = nenhum | 100% = sintomas graves',
    };
    return tooltips[key] || 'Percentagem de risco nesta dimensão';
  }

  registerIntervention(): void {
    this.interventionMessage = '';
    this.interventionError = '';

    if (!this.selectedPatientId) {
      this.interventionError = 'Selecione um paciente.';
      return;
    }

    const description = (this.recommendationText || '').trim();
    if (!description) {
      this.interventionError = 'Introduza recomendações ou notas.';
      return;
    }

    this.savingIntervention = true;
    this.interventionsService
      .create({ employee_id: this.selectedPatientId, description })
      .subscribe({
        next: () => {
          this.savingIntervention = false;
          this.interventionMessage = 'Intervenção registada com sucesso.';
          this.recommendationText = '';
        },
        error: (err) => {
          this.savingIntervention = false;
          this.interventionError = err?.message || 'Erro ao registar intervenção.';
        },
      });
  }

  getRiskBadgeClass(risk: string | null | undefined): string {
    if (!risk) return 'bg-gray-100 text-gray-800';
    const lower = risk.toString().toLowerCase();

    // High first (avoid matching "leve" inside "level")
    if (
      /\b5\b/.test(lower) ||
      /\b4\b/.test(lower) ||
      lower.includes('elevado') ||
      lower.includes('alto') ||
      lower.includes('high')
    ) {
      return 'bg-red-100 text-red-800';
    }

    // Moderate
    if (
      /\b3\b/.test(lower) ||
      /\b2\b/.test(lower) ||
      lower.includes('moderado') ||
      lower.includes('medium')
    ) {
      return 'bg-yellow-100 text-yellow-800';
    }

    // Low
    if (
      /\b1\b/.test(lower) ||
      lower.includes('baixo') ||
      lower.includes(' leve') ||
      lower.startsWith('leve') ||
      lower.includes('low')
    ) {
      return 'bg-green-100 text-green-800';
    }

    return 'bg-gray-100 text-gray-800';
  }

  getProgressBarClass(percent: number): string {
    if (percent >= 65) return 'bg-gradient-to-r from-red-500 to-red-600';
    if (percent >= 45) return 'bg-gradient-to-r from-yellow-500 to-yellow-600';
    return 'bg-gradient-to-r from-green-500 to-green-600';
  }
}
