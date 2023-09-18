async function resetPassword() {
    const url = "http://127.0.0.1:8000/public/users/password/reset";
    const data = {
        email: document.getElementById("email").value
    };

    const response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (response.status === 200) {
      window.newPass.showModal()
    }
}