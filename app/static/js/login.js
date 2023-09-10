async function loginUser() {
    const url = "http://localhost:8000/public/auth/login";
    const formData = new FormData();
    formData.append('username', document.getElementById('email').value);
    formData.append('password', document.getElementById('password').value);

    const response = await fetch(url, {
    method: 'POST',
    body: formData,
    credentials: 'include'
    });

    if (response.status === 201) {
        const responseData = await response.json();
        const url = `/pages/profile`;
        window.location.href = url;
    }
}