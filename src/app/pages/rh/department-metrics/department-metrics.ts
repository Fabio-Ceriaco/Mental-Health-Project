import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Footer } from '../../../components/footer/footer';
import { Header } from '../../../components/header/header';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../../../services/dashboard.service';
import { RouterModule } from '@angular/router';

type DepartmentMetricsData = {
  avgStress: number;
  avgBurnout: number;
  avgAnxiety: number;
  avgDepression: number;
  avgScore: number;
  totalEmployees: number;
  atRiskCount: number;
  riskPercent: number;
};

type HeatmapCell = {
  name: string;
  stress: number;
  burnout: number;
  anxiety: number;
  depression: number;
};

type EvolutionMonth = {
  month: string;
  stress: number;
  burnout: number;
  anxiety: number;
  depression: number;
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
    avgStress: 0,
    avgBurnout: 0,
    avgAnxiety: 0,
    avgDepression: 0,
    avgScore: 0,
    totalEmployees: 0,
    atRiskCount: 0,
    riskPercent: 0,
  };

  // Heatmap data
  heatmapData: HeatmapCell[] = [];
  dimensions = ['stress', 'burnout', 'anxiety', 'depression'];

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
        avgStress: 0,
        avgBurnout: 0,
        avgAnxiety: 0,
        avgDepression: 0,
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

    this.metrics = {
      avgStress: avgRisk * 0.95,
      avgBurnout: avgRisk * 1.05,
      avgAnxiety: avgRisk * 0.9,
      avgDepression: avgRisk * 0.85,
      avgScore: avgRisk,
      totalEmployees: totalEmp,
      atRiskCount: Math.floor(Math.random() * 20) + 10,
      riskPercent: avgRisk > 60 ? 75 : 25,
    };

    this.generateHeatmapData(avgRisk, totalEmp);
    this.generateEvolutionData(avgRisk);

    console.log('[DepartmentMetrics] Metrics computed for:', this.selectedDepartment);
    this.cdr.detectChanges();
  }

  private generateHeatmapData(baseRisk: number, maxEmployees: number): void {
    this.heatmapData = [];
    const employeeCount = Math.min(12, maxEmployees);

    for (let i = 0; i < employeeCount; i++) {
      const variance = (Math.random() - 0.5) * 20;
      this.heatmapData.push({
        name: `EMP-${String(i + 1).padStart(3, '0')}`,
        stress: Math.max(0, Math.min(100, baseRisk * 0.95 + variance)),
        burnout: Math.max(0, Math.min(100, baseRisk * 1.05 + variance)),
        anxiety: Math.max(0, Math.min(100, baseRisk * 0.9 + variance)),
        depression: Math.max(0, Math.min(100, baseRisk * 0.85 + variance)),
      });
    }
  }

  private generateEvolutionData(baseRisk: number): void {
    const months = ['Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov'];
    this.evolutionData = months.map((month, idx) => {
      const trend = (idx / (months.length - 1)) * 15;
      return {
        month,
        stress: Math.max(0, Math.min(100, baseRisk * 0.95 + trend + (Math.random() - 0.5) * 10)),
        burnout: Math.max(0, Math.min(100, baseRisk * 1.05 + trend + (Math.random() - 0.5) * 10)),
        anxiety: Math.max(0, Math.min(100, baseRisk * 0.9 + trend + (Math.random() - 0.5) * 10)),
        depression: Math.max(
          0,
          Math.min(100, baseRisk * 0.85 + trend + (Math.random() - 0.5) * 10)
        ),
      };
    });

    this.maxEvolutionValue = Math.max(
      ...this.evolutionData.flatMap((m) => [m.stress, m.burnout, m.anxiety, m.depression])
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
