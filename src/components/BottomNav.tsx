import './BottomNav.css';
import { Link } from 'react-router-dom'

const BottomNav = () => {

  return (
    <div className="bottomNav">
      <ul>
        <li className="fa fa-cloud-sun li_item"><Link to="/" className='link'>Weather</Link></li>

        <li className="fas fa-users li_item"><Link to="/community" className='link'>Community</Link></li>

        <li className="fa fa-gear li_item"><Link to="/profile" className='link'>Settings</Link></li>

      </ul>
    </div>
  )
}

export default BottomNav;
