// Configuración para producción
// IMPORTANTE: Ajusta estas URLs según tu deployment

export const environment = {
  production: true,
  // Opción 1: Si usas S3 + API en otro servidor
  // apiUrl: 'https://api.tu-dominio.com',
  
  // Opción 2: Si usas EC2 con todo (frontend + backend)
  apiUrl: 'https://tu-dominio.com/api',
  
  // Opción 3: URL relativa (sirve para ambos casos)
  // apiUrl: '/api',
};