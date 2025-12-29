import { ChangeDetectionStrategy, Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { LoginService } from '../../../services/login.service';
import {
  AlertsService,
  AlertsSummary,
  AlertItem,
  SeedAlertsResponse,
} from '../../../services/alerts.service';

@Component({
  selector: 'app-alerts-rh',
  imports: [Header, Footer, CommonModule],
  templateUrl: './alerts-rh.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export default class Alerts {
  loading = true;
  errorMessage = '';
  seeding = false;
  seedMessage = '';
  seedDetails: SeedAlertsResponse['alerts'] | null = null;
  userRole: string | null = null;

  // Data arrays bound to the UI
  harassmentStats: { label: string; count: number }[] = [];
  statusStats: { label: string; count: number }[] = [];
  statusStatsCoaching: { label: string; count: number }[] = [];
  statusStatsTraining: { label: string; count: number }[] = [];
  recentAlerts: AlertItem[] = [];

  // Base copies to apply panel-specific filters/sorts
  private statusBase: { label: string; count: number }[] = [];
  private statusBaseCoaching: { label: string; count: number }[] = [];
  private statusBaseTraining: { label: string; count: number }[] = [];

  // Filters and sorting per panel
  statusFilterPsych: 'Todos' | 'A Aguardar' | 'Em Andamento' | 'Realizados' = 'Todos';
  statusFilterCoaching: 'Todos' | 'A Aguardar' | 'Em Andamento' | 'Realizados' = 'Todos';
  statusFilterTraining: 'Todos' | 'A Aguardar' | 'Em Andamento' | 'Realizados' = 'Todos';

  sortDescPsych = true;
  sortDescCoaching = true;
  sortDescTraining = true;

  constructor(
    private alertsService: AlertsService,
    private cdr: ChangeDetectorRef,
    private loginService: LoginService
  ) {}

  ngOnInit(): void {
    // Get user role from localStorage
    const user = this.loginService.obterUser();
    this.userRole = user?.role_name || null;
    this.cdr.markForCheck();

    this.fetchSummary();
  }

  private fetchSummary(): void {
    this.loading = true;
    this.alertsService.getSummary().subscribe({
      next: (res: AlertsSummary) => {
        this.harassmentStats = (res.harassment || []).map((x) => ({
          label: x.label,
          count: Number(x.count || 0),
        }));

        const statuses = res.statuses || {};
        const base = [
          { label: 'A Aguardar', count: Number(statuses['A Aguardar'] || 0) },
          { label: 'Em Andamento', count: Number(statuses['Em Andamento'] || 0) },
          { label: 'Realizados', count: Number(statuses['Realizados'] || 0) },
        ];

        this.statusBase = [...base];
        this.statusBaseCoaching = [...base];
        this.statusBaseTraining = [...base];

        this.applyAllPanels();
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.errorMessage = err?.message || 'Erro a carregar os alertas.';
        this.cdr.markForCheck();
      },
    });

    this.alertsService.getRecent(10).subscribe({
      next: (res) => {
        this.recentAlerts = res.items || [];
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.errorMessage = err?.message || 'Erro a carregar alertas recentes.';
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  getTotal(arr: { label: string; count: number }[]): number {
    return (arr || []).reduce((sum, i) => sum + (Number(i.count) || 0), 0);
  }

  toggleSortPsych(): void {
    this.sortDescPsych = !this.sortDescPsych;
    this.applyPsych();
  }

  toggleSortCoaching(): void {
    this.sortDescCoaching = !this.sortDescCoaching;
    this.applyCoaching();
  }

  toggleSortTraining(): void {
    this.sortDescTraining = !this.sortDescTraining;
    this.applyTraining();
  }

  setFilterPsych(value: 'Todos' | 'A Aguardar' | 'Em Andamento' | 'Realizados') {
    this.statusFilterPsych = value;
    this.applyPsych();
  }

  setFilterCoaching(value: 'Todos' | 'A Aguardar' | 'Em Andamento' | 'Realizados') {
    this.statusFilterCoaching = value;
    this.applyCoaching();
  }

  setFilterTraining(value: 'Todos' | 'A Aguardar' | 'Em Andamento' | 'Realizados') {
    this.statusFilterTraining = value;
    this.applyTraining();
  }

  onFilterChangePsych(event: Event): void {
    const value = (event.target as HTMLSelectElement | null)?.value as
      | 'Todos'
      | 'A Aguardar'
      | 'Em Andamento'
      | 'Realizados'
      | undefined;
    if (value) {
      this.setFilterPsych(value);
    }
  }

  onFilterChangeCoaching(event: Event): void {
    const value = (event.target as HTMLSelectElement | null)?.value as
      | 'Todos'
      | 'A Aguardar'
      | 'Em Andamento'
      | 'Realizados'
      | undefined;
    if (value) {
      this.setFilterCoaching(value);
    }
  }

  onFilterChangeTraining(event: Event): void {
    const value = (event.target as HTMLSelectElement | null)?.value as
      | 'Todos'
      | 'A Aguardar'
      | 'Em Andamento'
      | 'Realizados'
      | undefined;
    if (value) {
      this.setFilterTraining(value);
    }
  }

  private applyAllPanels(): void {
    const sortHar = (a: { count: number }, b: { count: number }) => b.count - a.count;
    this.harassmentStats = [...this.harassmentStats].sort(sortHar);
    this.applyPsych();
    this.applyCoaching();
    this.applyTraining();
  }

  private applyPsych(): void {
    this.statusStats = this.applyPanel(this.statusBase, this.statusFilterPsych, this.sortDescPsych);
  }

  private applyCoaching(): void {
    this.statusStatsCoaching = this.applyPanel(
      this.statusBaseCoaching,
      this.statusFilterCoaching,
      this.sortDescCoaching
    );
  }

  private applyTraining(): void {
    this.statusStatsTraining = this.applyPanel(
      this.statusBaseTraining,
      this.statusFilterTraining,
      this.sortDescTraining
    );
  }

  private applyPanel(
    base: { label: string; count: number }[],
    filter: 'Todos' | 'A Aguardar' | 'Em Andamento' | 'Realizados',
    sortDesc: boolean
  ): { label: string; count: number }[] {
    const filterFn = (x: { label: string }) => filter === 'Todos' || x.label === filter;
    const sortFn = (a: { count: number }, b: { count: number }) =>
      sortDesc ? b.count - a.count : a.count - b.count;
    return [...base].filter(filterFn).sort(sortFn);
  }

  runSeed(): void {
    this.seeding = true;
    this.seedMessage = '';
    this.seedDetails = null;
    this.cdr.markForCheck();

    this.alertsService.seedFromAssessments().subscribe({
      next: (res: SeedAlertsResponse) => {
        this.seedDetails = res.alerts;
        const gen = Number(res.alerts?.generated || 0);
        const emp = Number(res.alerts?.employees_processed || 0);
        const reason = res.alerts?.reason;
        this.seedMessage =
          gen > 0
            ? `Gerados ${gen} alertas para ${emp} colaboradores.`
            : reason
            ? `Nenhum alerta gerado: ${reason}`
            : 'Nenhum alerta gerado.';
        this.seeding = false;
        this.fetchSummary(); // refresh summary and recent after seeding
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.seedMessage = err?.message || 'Erro ao gerar alertas.';
        this.seeding = false;
        this.cdr.markForCheck();
      },
    });
  }
}
