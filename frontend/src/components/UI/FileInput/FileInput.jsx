import React, { useState } from "react";
import axios from "axios";

const FileInput = () => {
    const [files, setFiles] = useState([]);

    const uploadFile = async () => {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);  // ✅ files!
        });

        try {
            const result = await axios.post("/api/upload", formData);
            console.log("✅ Загружено:", result.data);
        } catch (error) {
            console.log("❌ Ошибка:", error);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <input
                type="file"
                multiple
                onChange={e => setFiles(Array.from(e.target.files))}
            />
            <br /><br />
            <button onClick={uploadFile}>Загрузить файлы</button>
            <div>Выбрано файлов: {files.length}</div>
        </div>
    );
};

export default FileInput;
