import { apiClient } from './client';
import type { MedicationCreate, Reminder } from '../types';

export const prescriptionsApi = {
  uploadPhoto: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<MedicationCreate[]>('/prescriptions/upload-photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  
  createPrescription: (data: MedicationCreate) => 
    apiClient.post('/prescriptions/create-prescription', data),
  
  getReminders: async () => {
    const response = await apiClient.get<Record<string, Reminder>>('/prescriptions/get-reminders');
    return Object.entries(response.data).map(([id, data]) => ({ ...data, id }));
  },
  
  completeReminder: (reminderId: string) => 
    apiClient.patch(`/prescriptions/complete-reminder?reminder_id=${reminderId}`),
};
