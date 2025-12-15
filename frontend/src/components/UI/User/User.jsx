

import React from "react";
import cl from "./User.module.css"

const UserCard = ({name, lastname, id}) => {

    return (
        <div className={cl.UserCard}>   
            <ul>
                <li>Имя: {name}</li>
                <li>Фамилия: {lastname}</li>
                <li>ID: {id}</li>
            </ul>
        </div>
    )
}

export default UserCard