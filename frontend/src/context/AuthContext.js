import React, { createContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = sessionStorage.getItem('token');
        if (token) {
          api.defaults.headers.common['x-auth-token'] = token;
          const res = await api.get('/auth/verify');
          setUser(res.data);
          setIsAuthenticated(true);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (userData) => {
    try {
      const res = await api.post('/auth/login', userData);
      const { token } = res.data;
      sessionStorage.setItem('token', token);
      api.defaults.headers.common['x-auth-token'] = token;
      const userRes = await api.get('/auth/verify');
      setUser(userRes.data);
      setIsAuthenticated(true);
      return true;
    } catch (err) {
      console.error(err);
      return false;
    }
  };

  // Similar para register y logout usando sessionStorage
};

export { AuthContext, AuthProvider };