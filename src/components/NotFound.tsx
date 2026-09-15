import { Link } from 'react-router-dom';

const NotFound = () => (
  <div className="container">
    <h2>404 - Page not found</h2>
    <p>The page you asked for does not exist.</p>
    <Link to="/">Go to Weather</Link>
  </div>
);

export default NotFound;
