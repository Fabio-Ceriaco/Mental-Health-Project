import { LoginService } from '../../../services/login.service';
import { FormsModule } from '@angular/forms';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Header } from '../../../components/header/header';
import { Footer } from '../../../components/footer/footer';
import { ProfileService } from '../../../services/profile.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, Header, Footer, FormsModule],
  templateUrl: './profile.html',
  styleUrls: ['./profile.css'],
})
export default class Profile implements OnInit {
  profileData: any;
  form: any = {};
  isEditing: boolean = false;
  errorMsg: string = '';
  successMsg: string = '';
  genders: any[] = [];
  maritalStatuses: any[] = [];

  constructor(
    private route: ActivatedRoute,
    private profileService: ProfileService,
    private LoginService: LoginService,
    private router: Router
  ) {}

  //--------- Lifecycle Method ---------//
  ngOnInit(): void {
    this.profileData = this.route.snapshot.data['profileData'];

    if (!this.profileData) {
      this.errorMsg = 'Não foi possível carregar os dados do perfil.';
    }
    console.log(this.profileData);
    this.form = { ...this.profileData.profile };
    this.genders = this.profileData.options.genders;
    this.maritalStatuses = this.profileData.options.marital_status;
  }

  //--------- Profile Methods ---------//

  // // Reset form to initial profile data
  // resetForm() {
  //   this.form = {
  //     name: this.profileData.profile?.name ?? '',
  //     phone_number: this.profileData.profile?.phone_number ?? '',
  //     gender_label: this.profileData.profile?.gender_label,
  //     date_of_birth: this.profileData.profile?.date_of_birth ?? '',
  //     zip_code: this.profileData.profile?.zip_code ?? '',
  //     location: this.profileData.profile?.location ?? '',
  //     marital_status_label: this.profileData.profile?.marital_status_label ?? '',
  //     num_children: this.profileData.profile?.num_children ?? 0,
  //   };
  // }

  // edit profile

  edit() {
    this.isEditing = true;
    this.successMsg = '';
    this.errorMsg = '';
  }

  // cancel edit profile
  cancel() {
    this.form = { ...this.profileData.profile };
    this.genders = this.profileData.options.genders;
    this.maritalStatuses = this.profileData.options.marital_status;
    this.isEditing = false;
    this.successMsg = '';
    this.errorMsg = '';
  }

  // save profile

  save() {
    this.profileService.updateProfile(this.form).subscribe({
      next: (response) => {
        this.successMsg = 'Perfil atualizado com sucesso.';
        this.errorMsg = '';
        this.isEditing = false;
        this.profileData.profile = response;
      },
      error: (error) => {
        this.errorMsg = 'Erro ao atualizar o perfil. Por favor, tente novamente. ' + error.message;
        this.successMsg = '';
      },
    });
  }

  goBack() {
    this.router.navigate(['/employee/dashboard']);
  }
}
