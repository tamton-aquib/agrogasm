import './BottomNav.css';
import { Link } from 'react-router-dom'

const BottomNav = () => {

  return (
    <div className="bottomNav">
      <ul>
        <li className="fa fa-github li_item"><Link to="/Weather" className='link'>Weather</Link></li>

        <li className="fab fa-discord li_item"><Link to="/Community" className='link'>Community</Link></li>

        <li className="fas fa-cloud-sun li_item"><Link to="/Profile" className='link'>Profile</Link></li>

      </ul>
    </div>
  )
}

export default BottomNav;
