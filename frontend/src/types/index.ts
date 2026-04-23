export interface User {
  id: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface Medication {
  id: string;
  name: string;
  dosage: string;
  instructions: string | null;
  user_id: string;
}

export interface Reminder {
  id: string;
  medication_id: string;
  name: string;
  dosage: string;
  instructions: string | null;
  time: string;
  is_completed: boolean;
}

export interface MedicationCreate {
  name: string;
  dosage: string;
  instructions: string | null;
  start_time: string;
  end_time: string | null;
  nday: number;
  times: string[];
}
