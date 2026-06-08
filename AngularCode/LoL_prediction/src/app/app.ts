import { Component, OnDestroy, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { interval, startWith, Subject, switchMap, takeUntil } from 'rxjs';

import { Dashboard, DashboardService } from './dashboard-service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.sass'
})
export class App implements OnInit, OnDestroy {
  dashboardData?: Dashboard;
  errorMessage?: string;

  private destroy$ = new Subject<void>();

  constructor(
    private dashboardService: DashboardService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    interval(5000)
      .pipe(
        startWith(0),
        switchMap(() => this.dashboardService.getDashboard()),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (data: Dashboard) => {
          console.log('Dashboard updated:', data);
          this.dashboardData = data;
          this.errorMessage = undefined;

          this.cdr.detectChanges();
        },
        error: (error) => {
          console.error(error);
          this.errorMessage = 'Could not connect to backend.';

          this.cdr.detectChanges();
        }
      });
  }

  get isDashboardReady(): boolean {
    return this.dashboardData?.prediction?.status === 'success' &&
           this.dashboardData?.matchData?.status === 'success';
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}