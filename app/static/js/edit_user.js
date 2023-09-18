async function EditUser() {
    const url = "http://127.0.0.1:8000/private/users/update";
    const data = {
        name: document.getElementById("name").value,
        surname: document.getElementById("surname").value,
        description: document.getElementById("description").value,
        password: document.getElementById("password").value
    };

    const response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (response.status === 200) {
        const url = `/pages/profile`;
        window.location.href = url;
    }
}


async function getMe() {
    const url = "http://127.0.0.1:8000/private/users/me";

    const response = await fetch(url, {
    method: 'GET',
    credentials: 'include'
    });

    if (response.status === 200) {
        const responseData = await response.json();
        console.log(responseData)
        const nameInput = document.getElementById("name");
        const surnameInput = document.getElementById("surname");
        const descriptionInput = document.getElementById("description");
        nameInput.value = responseData.name
        surnameInput.value = responseData.surname
        descriptionInput.value = responseData.description
    } else if (response.status === 401) {
      // Если получен статус 401 (Unauthorized), вызвать функцию обновления пользователя
      await refreshToken();
      await getMe();
    } else {
      // Обработка других статусов ошибок
      console.error(`Failed to get user data. Status: ${response.status}`);
    }
}


document.addEventListener('DOMContentLoaded', async function() {
  await getMe();
});