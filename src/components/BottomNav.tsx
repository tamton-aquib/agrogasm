import './BottomNav.css';

const BottomNav = () => {
  return (
    <div className="bottomNav">
      <ul>
        <a target="_blank" href="https://github.com/tamton-aquib">
          <li className="fa fa-github li_item"></li>
        </a>
        <a target="_blank" href="https://discord.com/users/845674119391477820">
          <li className="fab fa-discord li_item"></li>
        </a>
        <a target="_blank" href="https://twitter.com/tamton_aquib">
          <li className="fas fa-cloud-sun li_item"></li>
        </a>
      </ul>
    </div>
  )
}

export default BottomNav;