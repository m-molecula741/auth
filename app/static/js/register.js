async function registerUser() {
        const url = "http://localhost:8000/public/users/registration";
        const data = {
            name: document.getElementById("name").value,
            surname: document.getElementById("surname").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.status === 201) {
            const responseData = await response.json();
            const id = responseData.id;
            const email = responseData.email;
            const url = `/pages/confirm?id=${id}&email=${email}`;
            window.location.href = url;
        }
    }