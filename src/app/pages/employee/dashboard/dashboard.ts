import { LoginService } from '../../../services/login.service';
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { DashboardService } from '../../../services/dashboard.service';
import { NgApexchartsModule } from 'ng-apexcharts';
import { CommonModule, formatDate } from '@angular/common';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { ActivatedRoute } from '@angular/router';
import { MLPrediction } from '../../../interfaces/api-responses';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [NgApexchartsModule, CommonModule, Header, Footer],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css'],
})
export default class Dashboard implements OnInit {
  employeeData: any = null;

  dashboardData: any = null;
  errorMsg: string = '';
  mlPrediction: MLPrediction | null = null;
  mlLoading: boolean = false;
  mlError: string = '';
  private mlTimeoutHandle: any = null;

  chartHistory: any = null;
  chartDimensions: any = null;
  chartRiskGauge: any = null;

  constructor(
    private loginService: LoginService,
    private dashboardService: DashboardService,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const emp = this.loginService.obterEmployee(); // Get the logged-in employee data
    if (!emp || !emp.id) {
      this.errorMsg = 'Employee not logged in.';
      return;
    }

    this.dashboardData = this.route.snapshot.data['dashboardData'];

    if (!this.dashboardData) {
      this.errorMsg = 'Failed to load dashboard data.';
      return;
    }
    this.buildCharts(this.dashboardData);
    this.loadMLPrediction(emp.id);
  }

  private loadMLPrediction(employeeId: number | string): void {
    this.mlLoading = true;
    this.mlError = '';
    if (this.mlTimeoutHandle) {
      clearTimeout(this.mlTimeoutHandle);
    }
    // Hard fallback in case the request never resolves
    this.mlTimeoutHandle = setTimeout(() => {
      if (this.mlLoading) {
        console.warn('[Dashboard] ML prediction timed out (fallback)');
        this.mlError = 'Tempo esgotado ao obter previsão de risco.';
        this.mlLoading = false;
      }
    }, 20000);
    console.log('[Dashboard] Requesting ML prediction for employee:', employeeId);
    this.dashboardService
      .getMLPrediction(employeeId)
      .pipe(
        finalize(() => {
          this.mlLoading = false;
          if (this.mlTimeoutHandle) {
            clearTimeout(this.mlTimeoutHandle);
            this.mlTimeoutHandle = null;
          }
          console.log(
            '[Dashboard] Finalize ML - loading:',
            this.mlLoading,
            'prediction:',
            this.mlPrediction
          );
          this.cdr.markForCheck();
        })
      )
      .subscribe({
        next: (prediction: MLPrediction) => {
          this.mlPrediction = prediction;
          console.log('[Dashboard] ML prediction received:', prediction);
          this.cdr.markForCheck();
        },
        error: (error) => {
          console.error('Failed to load ML prediction:', error);
          this.mlError = error.message || 'Failed to load risk prediction';
          this.cdr.markForCheck();
        },
      });
  }

  getRiskLevelColor(level: number): string {
    const colors: { [key: number]: string } = {
      1: '#4CAF50', // Green - Low risk
      2: '#8BC34A', // Light Green - Moderate risk
      3: '#FFC107', // Yellow - Medium risk
      4: '#FF9800', // Orange - High risk
      5: '#F44336', // Red - Critical risk
    };
    return colors[level] || '#9E9E9E';
  }

  getRiskLevelLabel(level: number): string {
    const labels: { [key: number]: string } = {
      1: 'Baixo Risco',
      2: 'Risco Moderado',
      3: 'Risco Médio',
      4: 'Alto Risco',
      5: 'Risco Crítico',
    };
    return labels[level] || 'Desconhecido';
  }

  // ----------Load Dashboard Data----------//

  private buildCharts(res: any) {
    const assessments = Array.isArray(res.per_assessment_results) // Check if data is array
      ? res.per_assessment_results
      : [];
    const categories = assessments.map((h: any) => formatDate(h.date, 'MM/yyyy', 'en-US')); // Format dates
    const scores = assessments.map((h: any) => Number(h.total_score ?? 0)); // Extract scores
    const maxTotalScore = assessments.length // Check if assessments exist
      ? Math.max(...assessments.map((a: any) => Number(a.total_score ?? 0))) //§ Get max score
      : 0;

    this.dashboardData.max_assessment_score = maxTotalScore; // Store max score in dashboardData

    this.chartHistory = {
      series: [{ name: 'Score por Questionário', data: scores }],
      chart: { type: 'line', height: 350 },
      xaxis: { categories, title: { text: 'Data do Questionário' } },
      stroke: { curve: 'smooth' },
      markers: { size: 2 },
      yaxis: [{ forceNiceScale: false, title: { text: 'Score' } }],
      tooltip: { enabled: true },
    };

    const perDim = res.per_dimension ?? {};
    const dimNames = Object.keys(perDim);
    const dimValues = Object.values(perDim).map((v: any) => Number(v.percent ?? 0));

    this.chartDimensions = {
      series: [{ names: 'Percentagem', data: dimValues }],
      chart: { type: 'bar', height: 250 },
      xaxis: { categories: dimNames },
      title: { text: 'Comparativo por Dimensão', align: 'center' },
    };

    const riskScore = res.overall?.score_total ?? 0;
    this.chartRiskGauge = {
      series: [riskScore],
      chart: { type: 'radialBar', height: 350 },
      plotOptions: {
        radialBar: {
          hollow: { size: '70%' },
          dataLabels: {
            name: { show: true },
            value: { show: true, formatter: (val: any) => `${val}` },
          },
        },
      },
      labels: [this.dashboardData.overall.risk_level],
    };
  }
}
