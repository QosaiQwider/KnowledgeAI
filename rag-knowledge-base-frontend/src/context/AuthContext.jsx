import {createContext,useContext,useState} from 'react';
import {api} from '../services/api';
const AuthContext=createContext(null);
export function AuthProvider({children}){
  const [token,setToken]=useState(localStorage.getItem('token'));
  const login=async(data)=>{ const r=await api.login(data); const t=r.access_token||r.token; if(!t) throw new Error('Backend did not return a token'); localStorage.setItem('token',t); setToken(t); return r; };
  const logout=()=>{localStorage.removeItem('token');setToken(null)};
  return <AuthContext.Provider value={{token,login,logout,isAuthenticated:!!token}}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext);
