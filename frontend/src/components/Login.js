import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link,
} from '@mui/material';
import { authAPI } from '../api';
import { useNavigate, Link as RouterLink } from 'react-router-dom';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await authAPI.register(username, password, name);
        // Автоматически логиним после регистрации
        await authAPI.login(username, password);
      } else {
        await authAPI.login(username, password);
      }
      navigate('/schedule');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при входе');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            {isRegister ? 'Регистрация' : 'Вход в Расписание ВГУ'}
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            {isRegister && (
              <TextField
                fullWidth
                label="Имя"
                value={name}
                onChange={(e) => setName(e.target.value)}
                margin="normal"
                required
              />
            )}

            <TextField
              fullWidth
              label="Логин"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              required
            />

            <TextField
              fullWidth
              label="Пароль"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Загрузка...' : isRegister ? 'Зарегистрироваться' : 'Войти'}
            </Button>

            <Box textAlign="center">
              <Link
                component="button"
                type="button"
                onClick={() => setIsRegister(!isRegister)}
                sx={{ cursor: 'pointer' }}
              >
                {isRegister
                  ? 'Уже есть аккаунт? Войти'
                  : 'Нет аккаунта? Зарегистрироваться'}
              </Link>
            </Box>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;