import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  TextField,
  IconButton,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  AttachFile as AttachFileIcon,
  Download as DownloadIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { scheduleAPI, filesAPI } from '../api';
import FileUpload from './FileUpload';

const Schedule = () => {
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingLesson, setEditingLesson] = useState(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedLessonId, setSelectedLessonId] = useState(null);

  // Загружаем расписание при изменении даты
  useEffect(() => {
    loadSchedule();
  }, [selectedDate]);

  const loadSchedule = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await scheduleAPI.createOrGetSchedule(selectedDate);
      setSchedule(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка загрузки расписания');
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  const handleLessonUpdate = async (lessonId, updates) => {
    try {
      await scheduleAPI.updateLesson(lessonId, updates);
      loadSchedule(); // Перезагружаем расписание
    } catch (err) {
      setError('Ошибка обновления пары');
    }
  };

  const handleLessonDelete = async (lessonId) => {
    if (window.confirm('Удалить эту пару?')) {
      try {
        await scheduleAPI.deleteLesson(lessonId);
        loadSchedule();
      } catch (err) {
        setError('Ошибка удаления пары');
      }
    }
  };

  const handleFileUpload = async (lessonId, files) => {
    try {
      await filesAPI.uploadToLesson(lessonId, files[0]);
      loadSchedule();
      setUploadDialogOpen(false);
    } catch (err) {
      setError('Ошибка загрузки файла');
    }
  };

  const handleFileDownload = async (fileId) => {
    try {
      await filesAPI.downloadFile(fileId);
    } catch (err) {
      setError('Ошибка скачивания файла');
    }
  };

  const handleFileDelete = async (fileId) => {
    if (window.confirm('Удалить файл?')) {
      try {
        await filesAPI.deleteFile(fileId);
        loadSchedule();
      } catch (err) {
        setError('Ошибка удаления файла');
      }
    }
  };

  const formatDate = (dateStr) => {
    try {
      return format(new Date(dateStr), 'dd MMMM yyyy', { locale: ru });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Расписание ВГУ
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Выбор даты */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <Typography variant="h6">
                Дата: {schedule ? formatDate(schedule.date) : ''}
              </Typography>
            </Grid>
            <Grid item>
              <TextField
                type="date"
                value={selectedDate}
                onChange={handleDateChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                onClick={loadSchedule}
                startIcon={<AddIcon />}
              >
                Обновить
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Список пар */}
        {schedule && schedule.lessons && (
          <Grid container spacing={3}>
            {schedule.lessons.map((lesson) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={lesson.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Пара {lesson.lesson_number}
                    </Typography>
                    
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Предмет: {lesson.subject || 'Не указан'}
                    </Typography>
                    
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Преподаватель: {lesson.teacher || 'Не указан'}
                    </Typography>
                    
                    <Typography variant="body2" color="textSecondary">
                      Аудитория: {lesson.room || 'Не указана'}
                    </Typography>

                    {/* Файлы */}
                    {lesson.files && lesson.files.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" gutterBottom>
                          Файлы:
                        </Typography>
                        {lesson.files.map((file) => (
                          <Chip
                            key={file.id}
                            label={file.filename}
                            onDelete={() => handleFileDelete(file.id)}
                            onClick={() => handleFileDownload(file.id)}
                            deleteIcon={<CloseIcon />}
                            sx={{ mr: 1, mb: 1, cursor: 'pointer' }}
                          />
                        ))}
                      </Box>
                    )}
                  </CardContent>

                  <CardActions>
                    <IconButton
                      size="small"
                      onClick={() => setEditingLesson(lesson)}
                    >
                      <EditIcon />
                    </IconButton>
                    
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedLessonId(lesson.id);
                        setUploadDialogOpen(true);
                      }}
                    >
                      <AttachFileIcon />
                    </IconButton>
                    
                    <IconButton
                      size="small"
                      onClick={() => handleLessonDelete(lesson.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* Диалог редактирования пары */}
      <Dialog
        open={!!editingLesson}
        onClose={() => setEditingLesson(null)}
      >
        {editingLesson && (
          <>
            <DialogTitle>
              Редактирование пары {editingLesson.lesson_number}
            </DialogTitle>
            <DialogContent>
              <TextField
                fullWidth
                label="Предмет"
                value={editingLesson.subject || ''}
                onChange={(e) =>
                  setEditingLesson({ ...editingLesson, subject: e.target.value })
                }
                margin="normal"
              />
              <TextField
                fullWidth
                label="Преподаватель"
                value={editingLesson.teacher || ''}
                onChange={(e) =>
                  setEditingLesson({ ...editingLesson, teacher: e.target.value })
                }
                margin="normal"
              />
              <TextField
                fullWidth
                label="Аудитория"
                value={editingLesson.room || ''}
                onChange={(e) =>
                  setEditingLesson({ ...editingLesson, room: e.target.value })
                }
                margin="normal"
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setEditingLesson(null)}>Отмена</Button>
              <Button
                onClick={() => {
                  handleLessonUpdate(editingLesson.id, {
                    subject: editingLesson.subject,
                    teacher: editingLesson.teacher,
                    room: editingLesson.room,
                  });
                  setEditingLesson(null);
                }}
                variant="contained"
              >
                Сохранить
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Диалог загрузки файла */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
      >
        <DialogTitle>Загрузить файл для пары</DialogTitle>
        <DialogContent>
          <FileUpload
            onUpload={(files) => handleFileUpload(selectedLessonId, files)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Отмена</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Schedule;