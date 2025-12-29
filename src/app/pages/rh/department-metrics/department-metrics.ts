import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Footer } from '../../../components/footer/footer';
import { Header } from '../../../components/header/header';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../../../services/dashboard.service';
import { RouterModule } from '@angular/router';

type DepartmentMetricsData = {
  dimensions: { [key: string]: number }; // Dynamic dimensions
  avgScore: number;
  totalEmployees: number;
  atRiskCount: number;
  riskPercent: number;
};

type HeatmapCell = {
  name: string;
  dimensions: { [key: string]: number }; // Dynamic dimensions
};

type EvolutionMonth = {
  month: string;
  dimensions: { [key: string]: number }; // Dynamic dimensions
};

@Component({
  selector: 'app-department-metrics',
  imports: [Header, Footer, CommonModule, RouterModule],
  templateUrl: './department-metrics.html',
})
export default class DepartmentMetrics implements OnInit {
  loading = true;
  errorMessage = '';

  departments: string[] = [];
  selectedDepartment = '';
  dropdownOpen = false;

  // Cache global data to avoid repeated API calls
  private globalData: any = null;

  metrics: DepartmentMetricsData = {
    dimensions: {},
    avgScore: 0,
    totalEmployees: 0,
    atRiskCount: 0,
    riskPercent: 0,
  };

  // Heatmap data
  heatmapData: HeatmapCell[] = [];

  // All 18 dimensions
  allDimensions = [
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

  // Top 4 dimensions to display in cards (can be dynamic based on highest values)
  topDimensions: string[] = ['stress', 'burnout', 'ansiedade', 'depressao'];

  // Evolution chart data
  evolutionData: EvolutionMonth[] = [];
  maxEvolutionValue = 100;

  constructor(private dashboardService: DashboardService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadDepartments();
  }

  loadDepartments(): void {
    this.loading = true;
    this.dashboardService.getGlobalDashboard().subscribe({
      next: (res: any) => {
        this.globalData = res;
        const deptMap = res.average_by_department || [];
        this.departments = deptMap.map((d: any) => d.department).sort();

        if (this.departments.length > 0) {
          this.selectedDepartment = this.departments[0];
          this.computeMetrics(res);
        }

        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.errorMessage = err?.message || 'Erro ao carregar departamentos.';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  loadMetricsForDepartment(globalData?: any): void {
    if (!this.selectedDepartment) return;

    if (globalData) {
      this.computeMetrics(globalData);
      this.cdr.detectChanges();
      return;
    }

    // Fallback: fetch if no cached data
    if (this.globalData) {
      this.computeMetrics(this.globalData);
      this.cdr.detectChanges();
    }
  }

  private computeMetrics(globalData: any): void {
    const deptData = globalData.average_by_department?.find(
      (d: any) => d.department === this.selectedDepartment
    );

    if (!deptData) {
      this.metrics = {
        dimensions: {},
        avgScore: 0,
        totalEmployees: 0,
        atRiskCount: 0,
        riskPercent: 0,
      };
      this.heatmapData = [];
      this.evolutionData = [];
      return;
    }

    const avgRisk = deptData.avg_risk || 0;
    const totalEmp = Math.floor(Math.random() * 50) + 50;

    // Generate mock dimension data
    const dimensions: { [key: string]: number } = {};
    this.allDimensions.forEach((dim) => {
      const variance = (Math.random() - 0.5) * 20;
      dimensions[dim] = Math.max(0, Math.min(100, avgRisk + variance));
    });

    this.metrics = {
      dimensions,
      avgScore: avgRisk,
      totalEmployees: totalEmp,
      atRiskCount: Math.floor(Math.random() * 20) + 10,
      riskPercent: avgRisk > 60 ? 75 : 25,
    };

    this.generateHeatmapData(avgRisk, totalEmp);
    this.generateEvolutionData(avgRisk);

    this.cdr.detectChanges();
  }

  private generateHeatmapData(baseRisk: number, maxEmployees: number): void {
    this.heatmapData = [];
    const employeeCount = Math.min(12, maxEmployees);

    for (let i = 0; i < employeeCount; i++) {
      const dimensions: { [key: string]: number } = {};
      this.allDimensions.forEach((dim) => {
        const variance = (Math.random() - 0.5) * 20;
        dimensions[dim] = Math.max(0, Math.min(100, baseRisk + variance));
      });

      this.heatmapData.push({
        name: `EMP-${String(i + 1).padStart(3, '0')}`,
        dimensions,
      });
    }
  }

  private generateEvolutionData(baseRisk: number): void {
    const months = ['Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov'];
    this.evolutionData = months.map((month, idx) => {
      const trend = (idx / (months.length - 1)) * 15;
      const dimensions: { [key: string]: number } = {};

      this.allDimensions.forEach((dim) => {
        dimensions[dim] = Math.max(0, Math.min(100, baseRisk + trend + (Math.random() - 0.5) * 10));
      });

      return {
        month,
        dimensions,
      };
    });

    this.maxEvolutionValue = Math.max(
      ...this.evolutionData.flatMap((m) => Object.values(m.dimensions))
    );
  }

  getHeatmapColor(value: number): string {
    if (value < 25) return 'bg-green-100';
    if (value < 50) return 'bg-yellow-100';
    if (value < 75) return 'bg-orange-100';
    return 'bg-red-100';
  }

  getHeatmapTextColor(value: number): string {
    if (value < 25) return 'text-green-900';
    if (value < 50) return 'text-yellow-900';
    if (value < 75) return 'text-orange-900';
    return 'text-red-900';
  }

  formatDimensionName(dimension: string): string {
    const dimensionLabels: { [key: string]: string } = {
      stress: 'Stress',
      ansiedade: 'Ansiedade',
      depressao: 'Depressão',
      burnout: 'Burnout',
      sono: 'Qualidade do Sono',
      turnos: 'Trabalho por Turnos',
      ergonomia: 'Ergonomia',
      carga_trabalho: 'Carga de Trabalho',
      equilibrio_vida: 'Equilíbrio Vida-Trabalho',
      reconhecimento: 'Reconhecimento',
      suporte_social: 'Suporte Social',
      lideranca: 'Liderança',
      seguranca_psicologica: 'Segurança Psicológica',
      seguranca_emprego: 'Segurança no Emprego',
      autonomia: 'Autonomia',
      proposito: 'Propósito no Trabalho',
      regulacao_emocional: 'Regulação Emocional',
      sintomas_fisicos: 'Sintomas Físicos',
    };
    return dimensionLabels[dimension] || dimension;
  }

  getDimensionColor(dimension: string): string {
    const colors: { [key: string]: string } = {
      stress: 'text-red-600',
      ansiedade: 'text-orange-600',
      depressao: 'text-purple-600',
      burnout: 'text-pink-600',
      sono: 'text-indigo-600',
      turnos: 'text-blue-600',
      ergonomia: 'text-cyan-600',
      carga_trabalho: 'text-yellow-600',
      equilibrio_vida: 'text-green-600',
      reconhecimento: 'text-lime-600',
      suporte_social: 'text-emerald-600',
      lideranca: 'text-teal-600',
      seguranca_psicologica: 'text-sky-600',
      seguranca_emprego: 'text-violet-600',
      autonomia: 'text-fuchsia-600',
      proposito: 'text-rose-600',
      regulacao_emocional: 'text-amber-600',
      sintomas_fisicos: 'text-red-700',
    };
    return colors[dimension] || 'text-gray-600';
  }

  getDimensionBgColor(dimension: string): string {
    const bgColors: { [key: string]: string } = {
      stress: 'bg-red-600',
      ansiedade: 'bg-orange-600',
      depressao: 'bg-purple-600',
      burnout: 'bg-pink-600',
      sono: 'bg-indigo-600',
      turnos: 'bg-blue-600',
      ergonomia: 'bg-cyan-600',
      carga_trabalho: 'bg-yellow-600',
      equilibrio_vida: 'bg-green-600',
      reconhecimento: 'bg-lime-600',
      suporte_social: 'bg-emerald-600',
      lideranca: 'bg-teal-600',
      seguranca_psicologica: 'bg-sky-600',
      seguranca_emprego: 'bg-violet-600',
      autonomia: 'bg-fuchsia-600',
      proposito: 'bg-rose-600',
      regulacao_emocional: 'bg-amber-600',
      sintomas_fisicos: 'bg-red-700',
    };
    return bgColors[dimension] || 'bg-gray-600';
  }

  getDimensionLightBgColor(dimension: string): string {
    const lightBgColors: { [key: string]: string } = {
      stress: 'bg-red-100',
      ansiedade: 'bg-orange-100',
      depressao: 'bg-purple-100',
      burnout: 'bg-pink-100',
      sono: 'bg-indigo-100',
      turnos: 'bg-blue-100',
      ergonomia: 'bg-cyan-100',
      carga_trabalho: 'bg-yellow-100',
      equilibrio_vida: 'bg-green-100',
      reconhecimento: 'bg-lime-100',
      suporte_social: 'bg-emerald-100',
      lideranca: 'bg-teal-100',
      seguranca_psicologica: 'bg-sky-100',
      seguranca_emprego: 'bg-violet-100',
      autonomia: 'bg-fuchsia-100',
      proposito: 'bg-rose-100',
      regulacao_emocional: 'bg-amber-100',
      sintomas_fisicos: 'bg-red-200',
    };
    return lightBgColors[dimension] || 'bg-gray-100';
  }

  getDimensionBorderColor(dimension: string): string {
    const borderColors: { [key: string]: string } = {
      stress: 'border-red-300',
      ansiedade: 'border-orange-300',
      depressao: 'border-purple-300',
      burnout: 'border-pink-300',
      sono: 'border-indigo-300',
      turnos: 'border-blue-300',
      ergonomia: 'border-cyan-300',
      carga_trabalho: 'border-yellow-300',
      equilibrio_vida: 'border-green-300',
      reconhecimento: 'border-lime-300',
      suporte_social: 'border-emerald-300',
      lideranca: 'border-teal-300',
      seguranca_psicologica: 'border-sky-300',
      seguranca_emprego: 'border-violet-300',
      autonomia: 'border-fuchsia-300',
      proposito: 'border-rose-300',
      regulacao_emocional: 'border-amber-300',
      sintomas_fisicos: 'border-red-400',
    };
    return borderColors[dimension] || 'border-gray-300';
  }

  toggleDropdown(): void {
    this.dropdownOpen = !this.dropdownOpen;
  }

  selectDepartment(dep: string): void {
    this.selectedDepartment = dep;
    this.dropdownOpen = false;
    this.cdr.detectChanges();

    // Use cached data for instant update
    if (this.globalData) {
      this.computeMetrics(this.globalData);
      this.cdr.detectChanges();
    }
  }
}
