from fastapi import FastAPI, File, UploadFile
from typing import List
import os
import shutil
from datetime import datetime
from time import sleep


app = FastAPI(title="Schedule API")


@app.get("/")
def root():
    return {"message": "API работает!"}

@app.get("/get_user")
async def get_user(user_id: int):
    users = [
        {'name': "Ivan", 'lastName': "remnev"},
        {'name': "Катя", 'lastName': "Шумакова"},
        {'name': "Кирилл", 'lastName': "Никитченко"}
    ]
    return users[user_id]

@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    os.makedirs("uploads", exist_ok=True)
    filenames = []
    
    for file in files:
   
        if file.filename:
            filename, file_ex = file.filename.rsplit('.', 1)
            filepath = f"uploads/{filename}{datetime.now()}.{file_ex}"
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            filenames.append(file.filename)
    
    return {"filenames": filenames, "count": len(filenames)}
