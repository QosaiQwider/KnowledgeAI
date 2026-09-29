import {NavLink,Outlet,useNavigate} from 'react-router-dom';
import {BookOpen,LayoutDashboard,LogOut,Sparkles} from 'lucide-react';
import {useAuth} from '../context/AuthContext';
export default function Layout(){const {logout}=useAuth();const nav=useNavigate();return <div className="shell"><aside className="sidebar"><div className="brand"><Sparkles size={22}/><span>KnowledgeAI</span></div><nav><NavLink to="/dashboard"><LayoutDashboard size={18}/>Dashboard</NavLink><NavLink to="/knowledge-bases"><BookOpen size={18}/>Knowledge Bases</NavLink></nav><button className="logout" onClick={()=>{logout();nav('/login')}}><LogOut size={18}/>Logout</button></aside><main className="main"><Outlet/></main></div>}
