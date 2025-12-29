import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../../../services/dashboard.service';
import { RouterLink } from '@angular/router';

type LatestEmployee = {
  employee_id: number;
  name: string;
  email: string;
  risk_level: number;
  score_percent: number;
};

type RiskDistribution = { risk: number; total: number };

type GlobalDashboard = {
  latest_per_employee: LatestEmployee[];
  global_distribution: RiskDistribution[];
  average_by_department: { department: string; avg_risk: number }[];
};

type Summary = {
  totalEmployees: number;
  avgScore: number;
  riskPercent: number;
  atRiskCount: number;
  departmentCount: number;
};

@Component({
  selector: 'app-rh-dashboard',
  imports: [Header, Footer, CommonModule, RouterLink],
  templateUrl: './rh-dashboard.html',
})
export default class RhDashboard implements OnInit {
  loading = true;
  errorMessage = '';
  data: GlobalDashboard | null = null;
  distribution: (RiskDistribution & { percent: number })[] = [];
  departments: { department: string; avg_risk: number; share: number }[] = [];
  summary: Summary = {
    totalEmployees: 0,
    avgScore: 0,
    riskPercent: 0,
    atRiskCount: 0,
    departmentCount: 0,
  };

  constructor(private dashboardService: DashboardService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.fetchDashboard();
  }

  private fetchDashboard(): void {
    this.loading = true;
    this.errorMessage = '';

    this.dashboardService.getGlobalDashboard().subscribe({
      next: (res: GlobalDashboard) => {
        console.log('Dashboard data received:', res);
        console.log('Global distribution:', res.global_distribution);

        this.data = res;
        this.summary = this.computeSummary(res);
        this.distribution = this.computeDistribution(res.global_distribution || []);

        console.log('Computed distribution:', this.distribution);

        this.departments = this.computeDepartments(res.average_by_department || []);
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.errorMessage = err?.message || 'Erro ao carregar dashboard.';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  private computeSummary(res: GlobalDashboard): Summary {
    const latest = res.latest_per_employee || [];
    const totalEmployees = latest.length;
    const totalScore = latest.reduce((acc, item) => acc + (Number(item.score_percent) || 0), 0);
    const avgScore = totalEmployees ? totalScore / totalEmployees : 0;

    const atRiskCount = latest.filter((item) => Number(item.risk_level) >= 3).length;
    const riskPercent = totalEmployees ? (atRiskCount / totalEmployees) * 100 : 0;

    const departmentCount = (res.average_by_department || []).length;

    return {
      totalEmployees,
      avgScore: Number(avgScore.toFixed(1)),
      riskPercent: Number(riskPercent.toFixed(1)),
      atRiskCount,
      departmentCount,
    };
  }

  private computeDistribution(
    list: RiskDistribution[]
  ): (RiskDistribution & { percent: number })[] {
    const total = list.reduce((acc, item) => acc + (Number(item.total) || 0), 0) || 1;
    return list.map((item) => ({
      ...item,
      percent: Number((((Number(item.total) || 0) / total) * 100).toFixed(1)),
    }));
  }

  private computeDepartments(
    list: { department: string; avg_risk: number }[]
  ): { department: string; avg_risk: number; share: number }[] {
    const max = list.reduce((acc, item) => Math.max(acc, Number(item.avg_risk) || 0), 0) || 1;
    return list.map((item) => ({
      ...item,
      share: Number((((Number(item.avg_risk) || 0) / max) * 100).toFixed(1)),
    }));
  }

  getRiskLabel(risk: any): string {
    // Handle string risk levels from backend
    const riskStr = String(risk).toLowerCase();

    if (riskStr.includes('sem risco') || riskStr.includes('nenhum')) {
      return 'Sem Risco';
    } else if (riskStr.includes('leve') || riskStr.includes('baixo')) {
      return 'Risco Leve';
    } else if (riskStr.includes('moderado')) {
      return 'Risco Moderado';
    } else if (riskStr.includes('elevado') || riskStr.includes('alto')) {
      return 'Risco Elevado';
    } else if (riskStr.includes('crítico') || riskStr.includes('critico')) {
      return 'Risco Crítico';
    }

    // Fallback: return the original value
    return String(risk);
  }

  getRiskColor(risk: any): string {
    // Handle string risk levels from backend
    const riskStr = String(risk).toLowerCase();

    if (riskStr.includes('sem risco') || riskStr.includes('nenhum')) {
      return 'bg-green-500';
    } else if (riskStr.includes('leve') || riskStr.includes('baixo')) {
      return 'bg-yellow-400';
    } else if (riskStr.includes('moderado')) {
      return 'bg-orange-500';
    } else if (riskStr.includes('elevado') || riskStr.includes('alto')) {
      return 'bg-red-500';
    } else if (riskStr.includes('crítico') || riskStr.includes('critico')) {
      return 'bg-red-700';
    }

    // Fallback
    return 'bg-gray-500';
  }
}
