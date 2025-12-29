import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-rgpd',
  imports: [],
  templateUrl: './rgpd.html',
  styleUrl: './rgpd.css',
})
export class Rgpd {
  @Output() closed = new EventEmitter<boolean>();
  @Output() consentGiven = new EventEmitter<boolean>();

  accept() {
    this.consentGiven.emit(true);
    this.closed.emit();
  }

  cancel() {
    this.consentGiven.emit(false);
    this.closed.emit();
  }
}
