import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { StudentView } from './views/StudentView';
import { StaffView } from './views/StaffView';
import { AdminView } from './views/AdminView';
import { LoginView } from './views/LoginView';
import { authService } from './services/auth';

export function App() {
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const user = authService.getCurrentUser();
    setCurrentUser(user);
  }, []);

  const handleLogout = () => {
    authService.logout();
    setCurrentUser(null);
  };

  if (!currentUser) {
    return <LoginView onLoginSuccess={(u) => setCurrentUser(u)} />;
  }

  return (
    <div className="app-container">
      <Navbar
        currentUser={currentUser}
        onUserChange={(u) => setCurrentUser(u)}
        onLogout={handleLogout}
      />

      <main className="main-content">
        {currentUser.role === 'Student' && <StudentView />}
        {currentUser.role === 'Staff' && <StaffView />}
        {currentUser.role === 'Admin' && <AdminView />}
      </main>

      <footer style={{ background: 'white', borderTop: '1px solid #e2e8f0', padding: '1rem', textAlign: 'center', fontSize: '0.8rem', color: '#64748b' }}>
        <strong>CampusOps</strong> • Final Year Cloud-Native Engineering Project • AWS Serverless Architecture (API Gateway + Lambda + DynamoDB + Cognito + S3) • Region: <code>ap-south-1</code>
      </footer>
    </div>
  );
}

export default App;
