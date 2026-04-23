import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { prescriptionsApi } from '../api/prescriptions';
import { Camera, Upload, Plus, X, Loader2, Calendar, Clock, ClipboardList } from 'lucide-react';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

const CreatePrescription = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    name: '',
    dosage: '',
    instructions: '',
    start_time: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
    end_time: '',
    nday: 0,
    times: [format(new Date(), "yyyy-MM-dd'T'08:00"), format(new Date(), "yyyy-MM-dd'T'20:00")]
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    const toastId = toast.loading('Распознаем рецепт...');
    try {
      const results = await prescriptionsApi.uploadPhoto(file);
      if (results && results.length > 0) {
        const data = results[0];
        setFormData({
          name: data.name || '',
          dosage: data.dosage || '',
          instructions: data.instructions || '',
          start_time: data.start_time ? data.start_time.slice(0, 16) : format(new Date(), "yyyy-MM-dd'T'HH:mm"),
          end_time: data.end_time ? data.end_time.slice(0, 16) : '',
          nday: data.nday || 0,
          times: data.times?.map(t => t.slice(0, 16)) || [format(new Date(), "yyyy-MM-dd'T'08:00")]
        });
        toast.success('Данные успешно извлечены!', { id: toastId });
      }
    } catch (error) {
      toast.error('Не удалось распознать фото', { id: toastId });
    } finally {
      setIsProcessing(false);
    }
  };

  const addTimeSlot = () => {
    setFormData(prev => ({
      ...prev,
      times: [...prev.times, format(new Date(), "yyyy-MM-dd'T'12:00")]
    }));
  };

  const removeTimeSlot = (index: number) => {
    setFormData(prev => ({
      ...prev,
      times: prev.times.filter((_, i) => i !== index)
    }));
  };

  const updateTimeSlot = (index: number, value: string) => {
    const newTimes = [...formData.times];
    newTimes[index] = value;
    setFormData(prev => ({ ...prev, times: newTimes }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await prescriptionsApi.createPrescription({
        ...formData,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: formData.end_time ? new Date(formData.end_time).toISOString() : null,
        times: formData.times.map(t => new Date(t).toISOString())
      });
      toast.success('Напоминания созданы!');
      navigate('/');
    } catch (error) {
      toast.error('Ошибка при создании');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Новое лекарство</h1>
        <p className="text-gray-500">Заполните форму или загрузите фото рецепта</p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {/* Upload Zone */}
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="p-8 border-b border-gray-100 bg-gray-50/50 hover:bg-gray-50 transition-colors cursor-pointer text-center group"
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            className="hidden" 
            accept="image/*" 
          />
          <div className="mx-auto w-16 h-16 bg-white rounded-2xl shadow-sm border border-gray-200 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            {isProcessing ? <Loader2 className="w-8 h-8 animate-spin text-primary" /> : <Camera className="w-8 h-8 text-primary" />}
          </div>
          <div className="font-bold text-gray-900">Загрузить фото рецепта</div>
          <p className="text-sm text-gray-500 mt-1">AI автоматически заполнит форму за вас</p>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <ClipboardList className="w-4 h-4 text-primary" />
                Название препарата
              </label>
              <input
                type="text"
                required
                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                placeholder="Напр: Ибупрофен"
                value={formData.name}
                onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">Дозировка</label>
              <input
                type="text"
                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                placeholder="Напр: 400 мг"
                value={formData.dosage}
                onChange={e => setFormData(prev => ({ ...prev, dosage: e.target.value }))}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700">Инструкции (необязательно)</label>
            <textarea
              className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none min-h-[80px]"
              placeholder="После еды, запить водой..."
              value={formData.instructions}
              onChange={e => setFormData(prev => ({ ...prev, instructions: e.target.value }))}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-gray-50">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-primary" />
                Дата начала
              </label>
              <input
                type="datetime-local"
                required
                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                value={formData.start_time}
                onChange={e => setFormData(prev => ({ ...prev, start_time: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">Дата окончания</label>
              <input
                type="datetime-local"
                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                value={formData.end_time}
                onChange={e => setFormData(prev => ({ ...prev, end_time: e.target.value }))}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700">Интервал (дни пропусков)</label>
            <div className="flex items-center gap-4">
              <input
                type="number"
                min="0"
                className="w-24 px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                value={formData.nday}
                onChange={e => setFormData(prev => ({ ...prev, nday: parseInt(e.target.value) || 0 }))}
              />
              <span className="text-sm text-gray-500">
                0 = ежедневно, 1 = через день
              </span>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-gray-50">
            <label className="text-sm font-semibold text-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary" />
                Время приема в первый день
              </div>
              <button 
                type="button" 
                onClick={addTimeSlot}
                className="text-primary hover:text-primary-dark font-medium flex items-center gap-1 transition-colors"
              >
                <Plus className="w-4 h-4" /> Добавить время
              </button>
            </label>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {formData.times.map((time, index) => (
                <div key={index} className="relative group">
                  <input
                    type="datetime-local"
                    required
                    className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                    value={time}
                    onChange={e => updateTimeSlot(index, e.target.value)}
                  />
                  {formData.times.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeTimeSlot(index)}
                      className="absolute -right-2 -top-2 bg-white border border-gray-200 text-gray-400 hover:text-red-500 rounded-full p-1 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || isProcessing}
            className="w-full flex items-center justify-center gap-2 py-4 bg-primary text-white rounded-xl font-bold hover:bg-primary-dark transition-all disabled:opacity-50 shadow-lg shadow-primary/20 mt-8"
          >
            {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
            {isSubmitting ? 'Создаем...' : 'Создать расписание'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreatePrescription;
