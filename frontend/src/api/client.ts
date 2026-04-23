import axios from 'axios';

// Если мы на localhost, используем /api (прокси Vite)
// Если мы зашли по внешней ссылке localtunnel, указываем URL бэкенда напрямую
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// ЗАМЕНИТЕ ЭТУ ССЫЛКУ на ту, которую выдаст npx localtunnel --port 8000
const REMOTE_BACKEND_URL = 'https://cold-forks-fail.loca.lt'; 

export const apiClient = axios.create({
  baseURL: isLocalhost ? '/api/v1' : `${REMOTE_BACKEND_URL}/api/v1`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Bypass-Tunnel-Reminder': 'true' // Помогает обходить заглушку localtunnel
  },
});
