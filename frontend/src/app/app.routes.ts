import { Routes } from '@angular/router';
import { HabitForm } from './components/habits/habit-form/habit-form';
import { Login } from './components/auth/login/login';
import { Register } from './components/auth/register/register';
import { Dashboard } from './components/dashboard/dashboard';
import { HabitList } from './components/habits/habit-list/habit-list';
import { Calendar } from './components/calendar/calendar';
import { Stats } from './components/stats/stats';
import { ExcelLoader } from './components/excel-loader/excel-loader';
import { AuthGuard } from './guards/auth.guard';
import { LoginGuard } from './guards/login.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'login', component: Login, canActivate: [LoginGuard] },
  { path: 'register', component: Register, canActivate: [LoginGuard] },
  { path: 'dashboard', component: Dashboard, canActivate: [AuthGuard] },
  { path: 'habits', component: HabitList, canActivate: [AuthGuard] },
  { path: 'habits/new', component: HabitForm, canActivate: [AuthGuard] },
  { path: 'habits/edit/:id', component: HabitForm, canActivate: [AuthGuard] },
  { path: 'calendar', component: Calendar, canActivate: [AuthGuard] },
  { path: 'stats', component: Stats, canActivate: [AuthGuard] },
  { path: 'excel-loader', component: ExcelLoader, canActivate: [AuthGuard] },
  { path: '**', redirectTo: '/dashboard' }
];