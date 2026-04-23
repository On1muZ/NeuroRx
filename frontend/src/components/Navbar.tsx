import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Pill, LogOut, PlusCircle, Bell } from 'lucide-react';
import { subscribeToPushNotifications } from '../lib/push';
import toast from 'react-hot-toast';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      toast.error('Ошибка при выходе');
    }
  };

  const handleSubscribe = async () => {
    const success = await subscribeToPushNotifications();
    if (success) {
      toast.success('Уведомления включены!');
    } else {
      toast.error('Не удалось включить уведомления');
    }
  };

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold text-primary">
          <Pill className="w-8 h-8" />
          <span>NeuroRx</span>
        </Link>
        
        <div className="flex items-center gap-4">
          <button 
            onClick={handleSubscribe}
            className="p-2 text-gray-600 hover:text-primary transition-colors"
            title="Включить уведомления"
          >
            <Bell className="w-5 h-5" />
          </button>
          
          <Link 
            to="/create" 
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Добавить</span>
          </Link>
          
          <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
            <span className="text-sm font-medium text-gray-700">{user?.username}</span>
            <button 
              onClick={handleLogout}
              className="p-2 text-gray-500 hover:text-red-500 transition-colors"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
