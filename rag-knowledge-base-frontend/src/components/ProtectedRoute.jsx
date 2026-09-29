import {Navigate} from 'react-router-dom';import {useAuth} from '../context/AuthContext';
export default function ProtectedRoute({children}){return useAuth().isAuthenticated?children:<Navigate to="/login" replace/>}
