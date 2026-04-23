import { useState, useEffect } from 'react';
import { prescriptionsApi } from '../api/prescriptions';
import { authApi } from '../api/auth';
import type { Reminder } from '../types';
import { CheckCircle2, Clock, Info, Loader2, AlertCircle, Send } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { ru } from 'date-fns/locale';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isTestingPush, setIsTestingPush] = useState(false);

  const fetchReminders = async () => {
    try {
      const data = await prescriptionsApi.getReminders();
      // Сортируем по времени
      const sorted = data.sort((a, b) => parseISO(a.time).getTime() - parseISO(b.time).getTime());
      setReminders(sorted);
    } catch (error) {
      toast.error('Не удалось загрузить напоминания');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReminders();
    // Обновляем каждую минуту
    const interval = setInterval(fetchReminders, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleTestPush = async () => {
    setIsTestingPush(true);
    try {
      await authApi.sendTestPush();
      toast.success('Тестовое уведомление отправлено!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка при отправке теста');
    } finally {
      setIsTestingPush(false);
    }
  };

  const handleComplete = async (id: string) => {
    try {
      await prescriptionsApi.completeReminder(id);
      toast.success('Принято!');
      fetchReminders();
    } catch (error) {
      toast.error('Ошибка при подтверждении');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ваши напоминания</h1>
          <div className="text-sm text-gray-500">
            На сегодня: {reminders.length}
          </div>
        </div>
        
        <button
          onClick={handleTestPush}
          disabled={isTestingPush}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-600 rounded-xl hover:text-primary hover:border-primary transition-all text-sm font-medium disabled:opacity-50"
        >
          {isTestingPush ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          Проверить уведомления
        </button>
      </div>

      {reminders.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-dashed border-gray-300">
          <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900">Нет активных напоминаний</h3>
          <p className="text-gray-500 mt-2">Загрузите фото рецепта или создайте расписание вручную</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reminders.map((reminder) => {
            const time = parseISO(reminder.time);
            const isOverdue = time < new Date() && !reminder.is_completed;

            return (
              <div 
                key={reminder.id}
                className={`bg-white rounded-2xl p-5 border transition-all flex items-center justify-between gap-4 ${
                  isOverdue ? 'border-red-200 bg-red-50/30' : 'border-gray-100'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl ${isOverdue ? 'bg-red-100 text-red-600' : 'bg-primary/10 text-primary'}`}>
                    <Clock className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold text-gray-900">{reminder.name}</h3>
                      <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs font-semibold rounded-full uppercase">
                        {reminder.dosage}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 mt-1">
                      <span className={`text-sm font-medium ${isOverdue ? 'text-red-600' : 'text-gray-500'}`}>
                        {format(time, 'HH:mm, d MMMM', { locale: ru })}
                      </span>
                      {reminder.instructions && (
                        <div className="flex items-center gap-1 text-sm text-gray-400">
                          <Info className="w-4 h-4" />
                          <span>{reminder.instructions}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {isOverdue && (
                    <div className="flex items-center gap-1 text-red-600 text-sm font-medium pr-2">
                      <AlertCircle className="w-4 h-4" />
                      <span>Пропущено!</span>
                    </div>
                  )}
                  <button
                    onClick={() => handleComplete(reminder.id)}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:border-primary hover:text-primary transition-all font-medium"
                  >
                    <CheckCircle2 className="w-5 h-5" />
                    <span>Принято</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
