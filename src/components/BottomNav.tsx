import './BottomNav.css';
import { NavLink } from 'react-router-dom'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'link active' : 'link';

const BottomNav = () => {
    return (
        <nav className="bottomNav" aria-label="Primary">
            <ul>
                <li><NavLink to="/" className={linkClass}><i className="fas fa-cloud-sun" aria-hidden="true"></i><span>Weather</span></NavLink></li>
                <li><NavLink to="/community" className={linkClass}><i className="fas fa-users" aria-hidden="true"></i><span>Community</span></NavLink></li>
                <li><NavLink to="/settings" className={linkClass}><i className="fa fa-gear" aria-hidden="true"></i><span>Settings</span></NavLink></li>
            </ul>
        </nav>
    )
}

export default BottomNav;
