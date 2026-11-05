/**
 * CampusOps Authentication Service
 * AWS Resource: Amazon Cognito User Pool client interface.
 * Handles user sessions, JWT tokens, and role-based permissions (Student, Staff, Admin).
 */

const STORAGE_KEY = 'campusops_auth_user';
const COGNITO_CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID || '';
const AWS_REGION = import.meta.env.VITE_AWS_REGION || 'ap-south-1';

export const DEMO_USERS = {
  Student: {
    user_id: 'usr-student-001',
    email: 'rahul.student@college.edu',
    name: 'Rahul Sharma (Student)',
    role: 'Student'
  },
  Staff: {
    user_id: 'usr-staff-002',
    email: 'ramesh.tech@college.edu',
    name: 'Ramesh Kumar (Maintenance Tech)',
    role: 'Staff'
  },
  Admin: {
    user_id: 'usr-admin-003',
    email: 'dean.admin@college.edu',
    name: 'Prof. S. Rao (Campus Administrator)',
    role: 'Admin'
  }
};

/**
 * Parses JWT token payload without external dependencies.
 */
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return {};
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return {};
  }
}

export const authService = {
  /**
   * Retrieves currently logged in user session from localStorage.
   * Only defaults to demo user in development / test environments.
   */
  getCurrentUser() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {
      console.error('Failed to read auth state from storage', e);
    }

    // In dev / test mode only, initialize default student session for testing
    if (import.meta.env.DEV) {
      const defaultUser = DEMO_USERS.Student;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultUser));
      return defaultUser;
    }

    return null;
  },

  /**
   * Logs in a user. Uses live Amazon Cognito if configured, or dev simulation.
   */
  async login(email, password, role = 'Student') {
    // 1. Live Amazon Cognito Authentication
    if (COGNITO_CLIENT_ID) {
      try {
        const cognitoEndpoint = `https://cognito-idp.${AWS_REGION}.amazonaws.com/`;
        const res = await fetch(cognitoEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
          },
          body: JSON.stringify({
            AuthFlow: 'USER_PASSWORD_AUTH',
            ClientId: COGNITO_CLIENT_ID,
            AuthParameters: {
              USERNAME: email.trim(),
              PASSWORD: password
            }
          })
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.message || data.__type || 'Cognito authentication failed');
        }

        const idToken = data.AuthenticationResult?.IdToken;
        const accessToken = data.AuthenticationResult?.AccessToken;
        const claims = parseJwt(idToken || '');

        const groups = claims['cognito:groups'] || [];
        let detectedRole = 'Student';
        if (groups.includes('Admin')) detectedRole = 'Admin';
        else if (groups.includes('Staff')) detectedRole = 'Staff';

        const user = {
          user_id: claims.sub || `usr-${Date.now().toString(36)}`,
          email: claims.email || email.trim(),
          name: claims.email ? claims.email.split('@')[0] : email.split('@')[0],
          role: detectedRole,
          token: idToken || accessToken
        };

        localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
        return user;
      } catch (err) {
        if (!import.meta.env.DEV) {
          throw err;
        }
        console.warn('Cognito login failed in dev, falling back to mock login:', err.message);
      }
    }

    // 2. Dev-only mock login
    if (import.meta.env.DEV) {
      const user = {
        user_id: `usr-${role.toLowerCase()}-${Date.now().toString(36)}`,
        email: email.trim(),
        name: email.split('@')[0],
        role: role,
        token: `mock-cognito-jwt-${Date.now()}`
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
      return user;
    }

    throw new Error('Authentication failed. Cognito Client ID not configured.');
  },

  /**
   * Switch roles dynamically (STRICTLY DEV ONLY).
   */
  switchRole(roleName) {
    if (!import.meta.env.DEV) {
      console.warn('Role switching is disabled in production.');
      return this.getCurrentUser();
    }
    const targetUser = DEMO_USERS[roleName] || DEMO_USERS.Student;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(targetUser));
    return targetUser;
  },

  /**
   * Clears session.
   */
  logout() {
    localStorage.removeItem(STORAGE_KEY);
  }
};
