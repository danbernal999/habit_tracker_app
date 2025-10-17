import { Routes } from '@angular/router';
import { HabitForm } from './components/habits/habit-form/habit-form';
import { Login } from './components/auth/login/login';
import { Register } from './components/auth/register/register';
import { Dashboard } from './components/dashboard/dashboard';
import { HabitList } from './components/habits/habit-list/habit-list';
import { Calendar } from './components/calendar/calendar';
import { Stats } from './components/stats/stats';
import { ExcelLoader } from './components/excel-loader/excel-loader';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'dashboard', component: Dashboard },
  { path: 'habits', component: HabitList },
  { path: 'habits/new', component: HabitForm },
  { path: 'habits/edit/:id', component: HabitForm },
  { path: 'calendar', component: Calendar },
  { path: 'stats', component: Stats },
  { path: 'excel-loader', component: ExcelLoader },
  { path: '**', redirectTo: '/login' }
];