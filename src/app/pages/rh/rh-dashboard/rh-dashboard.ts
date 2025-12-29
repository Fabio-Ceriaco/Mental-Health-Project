import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../../../services/dashboard.service';

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
  imports: [Header, Footer, CommonModule],
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
        this.data = res;
        this.summary = this.computeSummary(res);
        this.distribution = this.computeDistribution(res.global_distribution || []);
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
    // Handle boolean or numeric risk values
    if (risk === false || risk === 0 || risk === '0') {
      return 'Sem Risco';
    } else if (risk === true || risk === 1 || risk === '1') {
      return 'Em Risco';
    } else if (risk === 2 || risk === '2') {
      return 'Risco Moderado';
    } else if (risk === 3 || risk === '3') {
      return 'Risco Alto';
    } else if (risk === 4 || risk === '4') {
      return 'Risco Crítico';
    } else {
      return `Nível ${risk}`;
    }
  }

  getRiskColor(risk: any): string {
    // Handle boolean or numeric risk values
    if (risk === false || risk === 0 || risk === '0') {
      return 'bg-green-500';
    } else if (risk === true || risk === 1 || risk === '1') {
      return 'bg-yellow-500';
    } else if (risk === 2 || risk === '2') {
      return 'bg-orange-500';
    } else if (risk === 3 || risk === '3') {
      return 'bg-red-500';
    } else if (risk === 4 || risk === '4') {
      return 'bg-red-700';
    } else {
      return 'bg-gray-500';
    }
  }
}
