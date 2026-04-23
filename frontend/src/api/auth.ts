import { apiClient } from './client';
import type { User } from '../types';

export const authApi = {
  login: (username: string, password: string) => 
    apiClient.post('/users/login', { username, password }),
  
  signup: (username: string, password: string) => 
    apiClient.post('/users/signup', { username, password }),
  
  logout: () => 
    apiClient.post('/users/logout'),
  
  getMe: () => 
    apiClient.get<User>('/users/me'),
  
  getVapidKey: () => 
    apiClient.get<{ public_key: string }>('/users/vapid-public-key'),
  
  subscribePush: (subscription: any) => 
    apiClient.post('/users/subscribe-push', subscription),
  
  sendTestPush: () => 
    apiClient.post('/users/send-test-push'),
};
