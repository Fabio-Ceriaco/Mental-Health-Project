import { ChangeDetectionStrategy, Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { InterventionsService, InterventionCase } from '../../../services/interventions.service';

@Component({
  selector: 'app-active-cases',
  imports: [CommonModule, FormsModule, RouterModule, Header, Footer],
  templateUrl: './active-cases.html',
  styleUrls: ['./active-cases.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export default class ActiveCases {
  loading = true;
  errorMessage = '';
  searchTerm = '';
  deletingId: number | null = null;
  editingId: number | null = null;
  editFormData: { [key: number]: string } = {};
  allCases: InterventionCase[] = [];
  filteredCases: InterventionCase[] = [];

  constructor(private interventionsService: InterventionsService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.fetchActiveCases();
  }

  private fetchActiveCases(): void {
    this.loading = true;
    this.errorMessage = '';
    this.interventionsService.getAll().subscribe({
      next: (res) => {
        this.allCases = res.items || [];
        this.filteredCases = [...this.allCases];
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.errorMessage = err?.message || 'Erro a carregar casos ativos.';
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  onSearchChange(): void {
    const term = this.searchTerm.toLowerCase().trim();
    this.filteredCases = term
      ? this.allCases.filter(
          (c) =>
            (c.employee_name?.toLowerCase() || '').includes(term) ||
            c.employee_id.toString().includes(term) ||
            (c.intervention_action_name?.toLowerCase() || '').includes(term)
        )
      : [...this.allCases];
    this.cdr.markForCheck();
  }

  deleteIntervention(caseItem: InterventionCase): void {
    if (!caseItem?.id || this.deletingId === caseItem.id) {
      return;
    }
    this.deletingId = caseItem.id;
    this.errorMessage = '';
    this.cdr.markForCheck();

    this.interventionsService.delete(caseItem.id).subscribe({
      next: () => {
        this.allCases = this.allCases.filter((c) => c.id !== caseItem.id);
        this.onSearchChange();
        this.deletingId = null;
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        this.errorMessage = err?.message || 'Erro ao apagar intervenção.';
        this.deletingId = null;
        this.cdr.markForCheck();
      },
    });
  }

  openEditModal(caseItem: InterventionCase): void {
    this.editingId = caseItem.id;
    this.editFormData[caseItem.id] = caseItem.description;
    this.errorMessage = '';
    this.cdr.markForCheck();
  }

  cancelEdit(): void {
    this.editingId = null;
    this.editFormData = {};
    this.cdr.markForCheck();
  }

  saveEdit(caseItem: InterventionCase): void {
    if (!caseItem?.id || !this.editFormData[caseItem.id]?.trim()) {
      this.errorMessage = 'Descrição não pode estar vazia.';
      this.cdr.markForCheck();
      return;
    }

    this.interventionsService
      .update(caseItem.id, { description: this.editFormData[caseItem.id] })
      .subscribe({
        next: (updated) => {
          const idx = this.allCases.findIndex((c) => c.id === caseItem.id);
          if (idx !== -1) {
            this.allCases[idx] = {
              ...this.allCases[idx],
              description: updated.description,
              updated_at: updated.updated_at,
            };
          }
          this.onSearchChange();
          this.editingId = null;
          this.editFormData = {};
          this.cdr.markForCheck();
        },
        error: (err: any) => {
          this.errorMessage = err?.message || 'Erro ao atualizar intervenção.';
          this.cdr.markForCheck();
        },
      });
  }

  getEditingCase(): InterventionCase | undefined {
    return this.allCases.find((c) => c.id === this.editingId);
  }
}
