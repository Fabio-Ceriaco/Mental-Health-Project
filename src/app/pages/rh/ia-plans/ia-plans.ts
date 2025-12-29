import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { IAPlansService, IAPlan } from '../../../services/ia-plans.service';

@Component({
  selector: 'app-ia-plans',
  imports: [Header, Footer, CommonModule, FormsModule],
  templateUrl: './ia-plans.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export default class IaPlans implements OnInit {
  loading = true;
  errorMessage = '';
  generating = false;
  generateMessage = '';
  activeTab: 'acao' | 'impacto' | 'timeline' = 'acao';

  // All plans data
  allPlans: IAPlan[] = [];
  filteredPlans: IAPlan[] = [];

  // Selected plan
  selectedPlan: IAPlan | null = null;

  // Unique departments from plans
  departments: string[] = [];
  selectedDepartment = 'Todos';

  // Unique statuses from plans
  statusOptions: string[] = [];
  selectedStatus = 'Todos';

  constructor(private iaPlansService: IAPlansService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadPlans();
  }

  loadPlans(): void {
    this.loading = true;
    this.iaPlansService.getAllPlans().subscribe({
      next: (response) => {
        this.allPlans = response.items || [];
        this.filteredPlans = [...this.allPlans];

        // Extract unique departments
        const deptSet = new Set(this.allPlans.map((p) => p.department_name).filter((d) => d));
        this.departments = ['Todos', ...Array.from(deptSet).sort()];

        // Extract unique statuses
        const statusSet = new Set(this.allPlans.map((p) => p.status_name).filter((s) => s));
        this.statusOptions = ['Todos', ...Array.from(statusSet).sort()];

        // Auto-select first plan
        if (this.filteredPlans.length > 0) {
          this.selectedPlan = this.filteredPlans[0];
        }

        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.errorMessage = err?.message || 'Erro ao carregar planos de melhoria.';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  filterPlans(): void {
    this.filteredPlans = this.allPlans.filter((plan) => {
      const matchesDept =
        this.selectedDepartment === 'Todos' || plan.department_name === this.selectedDepartment;
      const matchesStatus =
        this.selectedStatus === 'Todos' || plan.status_name === this.selectedStatus;
      return matchesDept && matchesStatus;
    });

    // Auto-select first filtered plan
    if (
      this.filteredPlans.length > 0 &&
      (!this.selectedPlan || !this.filteredPlans.find((p) => p.id === this.selectedPlan?.id))
    ) {
      this.selectedPlan = this.filteredPlans[0];
    } else if (this.filteredPlans.length === 0) {
      this.selectedPlan = null;
    }

    this.cdr.detectChanges();
  }

  selectDepartment(dept: string): void {
    this.selectedDepartment = dept;
    this.filterPlans();
  }

  selectStatus(status: string): void {
    this.selectedStatus = status;
    this.filterPlans();
  }

  selectPlan(plan: IAPlan): void {
    this.selectedPlan = plan;
    this.activeTab = 'acao';
    this.cdr.detectChanges();
  }

  getStatusColor(status: string): string {
    const lower = status.toLowerCase();
    if (lower.includes('conclu') || lower.includes('aplicado'))
      return 'bg-green-100 text-green-800 border-green-200';
    if (lower.includes('execu') || lower.includes('andamento'))
      return 'bg-blue-100 text-blue-800 border-blue-200';
    if (lower.includes('espera') || lower.includes('aguard'))
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  }

  getImpactPercentage(): number {
    if (
      !this.selectedPlan?.impact_evaluation ||
      this.selectedPlan.impact_evaluation.before_index === 0
    ) {
      return 0;
    }
    const before = this.selectedPlan.impact_evaluation.before_index;
    const after = this.selectedPlan.impact_evaluation.after_index;
    return ((after - before) / before) * 100;
  }

  trackByPlanId(index: number, plan: IAPlan): number {
    return plan.id;
  }

  getDepartmentCount(): number {
    const set = new Set(this.filteredPlans.map((p) => p.department_name).filter(Boolean));
    return set.size;
  }

  getStatusCount(keyword: string): number {
    const k = keyword.toLowerCase();
    return this.filteredPlans.filter((p) => (p.status_name || '').toLowerCase().includes(k)).length;
  }

  setTab(tab: 'acao' | 'impacto' | 'timeline'): void {
    this.activeTab = tab;
    this.cdr.detectChanges();
  }

  generateAIPlans(): void {
    this.generating = true;
    this.generateMessage = '';
    this.cdr.detectChanges();

    this.iaPlansService.generateAIPlans().subscribe({
      next: (response) => {
        this.generating = false;
        this.generateMessage = response.message || 'Planos gerados com sucesso!';

        // Show details if available
        if (response.data) {
          const details = `${response.data.plans_generated} novos planos criados para ${
            response.data.departments_at_risk?.length || 0
          } departamentos.`;
          this.generateMessage += ' ' + details;
        }

        // Reload plans to show new ones
        setTimeout(() => {
          this.loadPlans();
        }, 1500);

        this.cdr.detectChanges();
      },
      error: (err) => {
        this.generating = false;
        this.generateMessage = 'Erro ao gerar planos: ' + (err?.message || 'Erro desconhecido');
        this.cdr.detectChanges();
      },
    });
  }
}
