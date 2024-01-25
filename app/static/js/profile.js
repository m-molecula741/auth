async function logoutUser() {
    const url = "http://127.0.0.1:8000/private/auth/logout";

    const response = await fetch(url, {
    method: 'POST',
    credentials: 'include'
    });

    if (response.status === 200) {
        const url = `/pages/login`;
        window.location.href = url;
    } else if (response.status === 401) {
      // Если получен статус 401 (Unauthorized), вызвать функцию обновления пользователя
      await refreshToken();
      await logoutUser();
    }
}


async function deleteUser() {
    const url = "http://127.0.0.1:8000/private/users/deactivate";

    const response = await fetch(url, {
    method: 'POST',
    credentials: 'include'
    });

    if (response.status === 200) {
        const url = `/pages/login`;
        window.location.href = url;
    } else if (response.status === 401) {
      // Если получен статус 401 (Unauthorized), вызвать функцию обновления пользователя
      await refreshToken();
      await logoutUser();
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
        const userInfoElement = document.getElementById("user-info");
        const emailElement = document.getElementById("email");
        const descriptionElement = document.getElementById("description");
        const createdElement = document.getElementById("created_ad");
        userInfoElement.innerHTML = `${responseData.name} ${responseData.surname}`;
        emailElement.innerHTML = `${responseData.email}`;
        descriptionElement.innerHTML = `${responseData.description}`;
        createdElement.innerHTML = `${responseData.created_at}`;
    } else if (response.status === 401) {
      // Если получен статус 401 (Unauthorized), вызвать функцию обновления пользователя
      await refreshToken();
      await getMe();
    } else {
      // Обработка других статусов ошибок
      console.error(`Failed to get user data. Status: ${response.status}`);
    }
}


async function EditRedirect() {
    await getMe();
    const url = `/pages/edit/user`;
    window.location.href = url;
}


async function toggleButtons() {
  var menu = document.querySelector('.menu');

  if (menu.style.display === 'none') {
    menu.style.display = 'block';
  } else {
    menu.style.display = 'none';
  }
}


async function refreshToken() {
  const response = await fetch('http://127.0.0.1:8000/public/auth/refresh', {
    method: 'POST',
  });

  if (response.ok) {
    const new_access_token = await response.json();
    return new_access_token.access_token;
  } else {
    throw new Error('Failed to refresh access token');
  }
}


document.addEventListener('DOMContentLoaded', async function() {
  await getMe();
  await toggleButtons();
});
