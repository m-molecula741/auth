async function confirmUser() {
            const url = "http://localhost:8000/public/users/registration/confirm";
            const data = {
            code: document.getElementById("code").value
            };

            await fetch(url, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
            }).then(response => {
                if (response.status === 200) {
                    window.location.href = "/pages/login"
                }
            });
        }
async function resendEmail() {
    const url = "http://localhost:8000/public/users/resending";
    const data = {
    id: '{{ id }}',
    email: '{{ email }}'
    };

    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
    }).then(response => {
        if (response.status === 200) {
            const id = '{{ id }}';
            const email = '{{ email }}';
            const url = `/pages/confirm?id=${id}&email=${email}`;
            window.location.href = url
        }
    });
}