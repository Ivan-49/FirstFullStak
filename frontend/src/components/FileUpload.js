import React, { useState } from 'react';
import {
  Box,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  LinearProgress,
} from '@mui/material';
import { Delete as DeleteIcon, CloudUpload as UploadIcon } from '@mui/icons-material';

const FileUpload = ({ onUpload, multiple = false }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setProgress(0);
    
    // Симуляция прогресса загрузки
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
    
    try {
      await onUpload(files);
      setFiles([]);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      clearInterval(interval);
      setUploading(false);
      setProgress(0);
    }
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  return (
    <Box>
      <Button
        variant="outlined"
        component="label"
        startIcon={<UploadIcon />}
        disabled={uploading}
        sx={{ mb: 2 }}
      >
        Выбрать файл{multiple ? 'ы' : ''}
        <input
          type="file"
          hidden
          onChange={handleFileChange}
          multiple={multiple}
        />
      </Button>

      {files.length > 0 && (
        <List>
          {files.map((file, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={file.name}
                secondary={`${(file.size / 1024).toFixed(2)} KB`}
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => removeFile(index)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}

      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2" align="center" sx={{ mt: 1 }}>
            {progress}% загружено
          </Typography>
        </Box>
      )}

      {files.length > 0 && !uploading && (
        <Button
          variant="contained"
          onClick={handleUpload}
          sx={{ mt: 2 }}
          fullWidth
        >
          Загрузить
        </Button>
      )}
    </Box>
  );
};

export default FileUpload;