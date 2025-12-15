import './App.css';
import axios from 'axios';
import { useState } from 'react';
import UserCard from './components/UI/User/User';
import FileInput from './components/UI/FileInput/FileInput';

function App() {
    const [doc, setDoc] = useState('');
    const [user, setUser] = useState(
        {
            user_id: 0,
            name: '',
            lastname:''
        })

    const getDocs = async () => {
        const result = await axios.get("/api/get_user", {
            params: { user_id: user.user_id}
        });
        setUser({...result.data, user_id: user.user_id})
        console.log(result)
    };

    return (
        <div className="App">
            <button onClick={getDocs}>Получить данные</button>
            <pre>{doc}</pre>

            <input 
            type='number' 
            value={user.user_id}
            onChange={e=> setUser({...user, user_id: parseInt(e.target.value)})}
            placeholder='id пользователя'
            >
            </input>

            <UserCard 
            name = {user.name}
            lastname={user.lastName}
            id = {user.user_id}
            >

            </UserCard>

            <div className='user'>
                
                id: {user.user_id}
                Имя: {user.name}
                Фамилия: {user.lastname}
            </div>

            <FileInput></FileInput>

        </div>
    );
}

export default App;
