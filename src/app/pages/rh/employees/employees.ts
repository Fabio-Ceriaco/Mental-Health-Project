import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EmployeeService, EmployeeCreatePayload } from '../../../services/employee.service';
import { Employee } from '../../../interfaces/employee.model';
import { Header } from '../../../components/header/header';

@Component({
  selector: 'app-employees',
  standalone: true,
  imports: [CommonModule, FormsModule, Header],
  templateUrl: './employees.html',
})
export default class Employees implements OnInit {
  employees: Employee[] = [];
  filtered: Employee[] = [];
  paginatedEmployees: Employee[] = [];
  searchId: string = '';
  searchName: string = '';
  creating = false;
  loading = false;
  errorMessage = '';
  successMessage = '';
  currentYear: number = new Date().getFullYear();
  Math = Math; // Make Math available in template

  // Pagination
  currentPage = 1;
  itemsPerPage = 50;
  totalPages = 1;

  newEmployee: EmployeeCreatePayload = {
    name: '',
    email: '',
    phone_number: '',
    gender_id: 1,
    date_of_birth: '',
    zip_code: '',
    location: '',
    marital_status_id: 1,
    num_children: 0,
    hire_date: '',
    contract_type_id: 1,
    department_id: 1,
    role_id: 3,
  };

  constructor(private employeeService: EmployeeService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadEmployees();
  }

  loadEmployees(): void {
    this.loading = true;
    this.errorMessage = '';
    this.cdr.detectChanges();

    this.employeeService.getAll().subscribe({
      next: (items) => {
        this.employees = items;
        this.filtered = items;
        this.currentPage = 1;
        this.updatePagination();
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Employees load failed:', err.message || err);
        this.errorMessage = err.message || 'Erro ao carregar funcionários';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  applyFilter(): void {
    const idTerm = this.searchId.trim();
    const nameTerm = this.searchName.trim().toLowerCase();

    if (!idTerm && !nameTerm) {
      this.filtered = this.employees;
    } else {
      this.filtered = this.employees.filter((e) => {
        const idMatch = !idTerm || String(e.id).includes(idTerm);
        const nameMatch = !nameTerm || e.name.toLowerCase().includes(nameTerm);
        return idMatch && nameMatch;
      });
    }

    this.currentPage = 1;
    this.updatePagination();
  }

  updatePagination(): void {
    this.totalPages = Math.ceil(this.filtered.length / this.itemsPerPage);
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    this.paginatedEmployees = this.filtered.slice(start, end);
    this.cdr.markForCheck();
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.updatePagination();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  get pageNumbers(): number[] {
    const pages = [];
    const maxVisible = 5;
    let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(this.totalPages, start + maxVisible - 1);

    if (end - start < maxVisible - 1) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }

  resetForm(): void {
    this.newEmployee = {
      name: '',
      email: '',
      phone_number: '',
      gender_id: 1,
      date_of_birth: '',
      zip_code: '',
      location: '',
      marital_status_id: 1,
      num_children: 0,
      hire_date: '',
      contract_type_id: 1,
      department_id: 1,
      role_id: 3,
    };
  }

  trackByEmployeeId(index: number, employee: Employee): number {
    return employee.id;
  }

  toggleCreate(): void {
    this.creating = !this.creating;
    this.successMessage = '';
    this.errorMessage = '';
    if (this.creating) this.resetForm();
  }

  saveNew(): void {
    // Quick validation for required fields
    const required = [
      'name',
      'email',
      'phone_number',
      'date_of_birth',
      'zip_code',
      'location',
      'hire_date',
    ] as const;
    for (const k of required) {
      const v = this.newEmployee[k];
      if (!v || String(v).trim() === '') {
        alert(`Campo obrigatório: ${k}`);
        return;
      }
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';
    this.employeeService.create(this.newEmployee).subscribe({
      next: (response) => {
        console.log('Employee created successfully:', response);
        this.creating = false;
        this.loading = false;
        this.successMessage = 'Funcionário criado com sucesso!';
        console.log('Success message set to:', this.successMessage);
        // Auto-clear success message after 5 seconds
        setTimeout(() => {
          this.successMessage = '';
        }, 5000);
        // Load employees in background
        this.loadEmployees();
      },
      error: (err) => {
        console.error('Error creating employee:', err);
        this.errorMessage = `Erro a criar funcionário: ${err.message || err}`;
        this.loading = false;
      },
    });
  }
}
