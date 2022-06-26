import './BottomNav.css';
import { Link } from 'react-router-dom'

const BottomNav = () => {

    return (
        <div className="bottomNav">
            <ul>
                <li className="fa fa-github li_item"><Link to="/weather" className='link'>Weather</Link></li>
                <li className="fab fa-discord li_item"><Link to="/community" className='link'>Community</Link></li>
                <li className="fas fa-cloud-sun li_item"><Link to="/profile" className='link'>Profile</Link></li>
            </ul>
        </div>
    )
}

export default BottomNav;
