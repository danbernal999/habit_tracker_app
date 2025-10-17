import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ExcelService } from '../../services/excel';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-excel-loader',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './excel-loader.html',
  styleUrls: ['./excel-loader.css']
})
export class ExcelLoader implements OnInit, OnDestroy {
  // Archivo seleccionado
  selectedFile: File | null = null;
  fileName: string = '';
  fileSize: string = '';

  // Estado de UI
  activeTab: 'upload' | 'manage' = 'upload';
  isUploading: boolean = false;
  progress: number = 0;
  uploadStatus: 'idle' | 'uploading' | 'success' | 'error' = 'idle';
  errorMessage: string = '';
  successMessage: string = '';
  rowsProcessed: number = 0;

  // Gestión de archivos
  files: any[] = [];
  isLoadingFiles: boolean = false;
  excelData: any[] = [];
  totalRecords: number = 0;
  currentPage: number = 1;
  pageSize: number = 10;

  private destroy$ = new Subject<void>();

  constructor(private excelService: ExcelService) {}

  ngOnInit(): void {
    this.loadFiles();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.excelService.disconnectProgressWebSocket();
  }

  /**
   * Cambiar pestaña
   */
  switchTab(tab: 'upload' | 'manage'): void {
    this.activeTab = tab;
    if (tab === 'manage') {
      this.loadFiles();
    }
  }

  /**
   * Manejar selección de archivo
   */
  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectFile(file);
    }
  }

  /**
   * Seleccionar archivo
   */
  selectFile(file?: File): void {
    if (!file) {
      this.errorMessage = 'No se seleccionó ningún archivo';
      return;
    }

    if (!file.name.match(/\.(xls|xlsx)$/)) {
      this.errorMessage = 'Solo se permiten archivos .xls o .xlsx';
      return;
    }

    this.selectedFile = file;
    this.fileName = file.name;
    this.fileSize = this.formatFileSize(file.size);
    this.errorMessage = '';
  }

  /**
   * Limpiar archivo seleccionado
   */
  clearFile(): void {
    this.selectedFile = null;
    this.fileName = '';
    this.fileSize = '';
  }

  /**
   * Cargar archivo
   */
  uploadFile(): void {
    if (!this.selectedFile) {
      this.errorMessage = 'Selecciona un archivo primero';
      return;
    }

    this.isUploading = true;
    this.uploadStatus = 'uploading';
    this.progress = 0;
    this.errorMessage = '';

    // Conectar WebSocket para monitorear progreso
    this.excelService.connectProgressWebSocket();

    // Escuchar actualizaciones de progreso
    this.excelService.progress$
      .pipe(takeUntil(this.destroy$))
      .subscribe(progress => {
        this.progress = progress;
      });

    // Subir archivo
    this.excelService.uploadExcel(this.selectedFile!)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.uploadStatus = 'success';
          this.successMessage = `Archivo procesado exitosamente. ${response.rows_processed} filas procesadas.`;
          this.rowsProcessed = response.rows_processed;
          this.isUploading = false;
          this.resetForm();
        },
        error: (error) => {
          this.uploadStatus = 'error';
          this.errorMessage = error.error?.error || 'Error al cargar el archivo';
          this.isUploading = false;
        }
      });
  }

  /**
   * Reiniciar formulario
   */
  resetForm(): void {
    this.selectedFile = null;
    this.fileName = '';
    this.fileSize = '';
    this.progress = 0;
    this.uploadStatus = 'idle';
    this.isUploading = false;
  }

  /**
   * Cargar lista de archivos
   */
  loadFiles(): void {
    this.isLoadingFiles = true;
    this.excelService.listUploadedFiles()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.files = response.files || [];
          this.isLoadingFiles = false;
          if (this.files.length > 0) {
            this.loadExcelData();
          }
        },
        error: (error) => {
          console.error('Error loading files:', error);
          this.isLoadingFiles = false;
        }
      });
  }

  /**
   * Cargar datos de Excel
   */
  loadExcelData(): void {
    const offset = (this.currentPage - 1) * this.pageSize;
    this.excelService.getExcelData(this.pageSize, offset)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.excelData = response.data || [];
          this.totalRecords = response.total || 0;
        },
        error: (error) => {
          console.error('Error loading excel data:', error);
        }
      });
  }

  /**
   * Eliminar archivo
   */
  deleteFile(filename: string): void {
    if (confirm(`¿Seguro que deseas eliminar ${filename}?`)) {
      this.excelService.deleteFile(filename)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.loadFiles();
          },
          error: (error) => {
            alert('Error al eliminar archivo');
          }
        });
    }
  }

  /**
   * Eliminar todos los datos
   */
  deleteAllData(): void {
    if (confirm('¿Seguro que deseas eliminar TODOS los datos? Esta acción no se puede deshacer.')) {
      this.excelService.deleteAllData()
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.files = [];
            this.excelData = [];
            this.totalRecords = 0;
            this.loadFiles();
          },
          error: (error) => {
            alert('Error al eliminar datos');
          }
        });
    }
  }

  /**
   * Descargar archivo
   */
  downloadFile(filename: string): void {
    this.excelService.downloadFile(filename);
  }

  /**
   * Cambiar página
   */
  changePage(page: number): void {
    if (page > 0 && page <= this.getTotalPages()) {
      this.currentPage = page;
      this.loadExcelData();
    }
  }

  /**
   * Obtener número total de páginas
   */
  getTotalPages(): number {
    return Math.ceil(this.totalRecords / this.pageSize);
  }

  /**
   * Obtener array de páginas para paginación
   */
  getPages(): number[] {
    const pages = [];
    const totalPages = this.getTotalPages();
    const maxPagesToShow = 5;

    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const startPage = Math.max(1, this.currentPage - Math.floor(maxPagesToShow / 2));
      const endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

      if (startPage > 1) {
        pages.push(1);
        if (startPage > 2) pages.push(0); // 0 representa "..."
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      if (endPage < totalPages) {
        if (endPage < totalPages - 1) pages.push(0);
        pages.push(totalPages);
      }
    }

    return pages;
  }

  /**
   * Formatear tamaño de archivo
   */
  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Obtener columnas de los datos
   */
  getColumns(): string[] {
    if (this.excelData.length === 0) return [];
    return Object.keys(this.excelData[0]).filter(key => key !== 'id');
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      this.selectFile(file);
    }
  }
}