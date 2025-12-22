// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { authAPI } from './api';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/Login';
import Schedule from './components/Schedule';
import Navbar from './components/Navbar';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/schedule"
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Schedule />
                </>
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <Navigate to={authAPI.isAuthenticated() ? "/schedule" : "/login"} />
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
};

export default App;