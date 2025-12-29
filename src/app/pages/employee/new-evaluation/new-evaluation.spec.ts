import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewEvaluation } from './new-evaluation';

describe('NewEvaluation', () => {
  let component: NewEvaluation;
  let fixture: ComponentFixture<NewEvaluation>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewEvaluation],
    }).compileComponents();

    fixture = TestBed.createComponent(NewEvaluation);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
