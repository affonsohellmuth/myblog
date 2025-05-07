// login.js - Place this in your static/js folder

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                // Format data as form-urlencoded which is what FastAPI expects
                const formData = new URLSearchParams();
                formData.append('username', username);
                formData.append('password', password);
                
                // Send authentication request
                const response = await fetch('/token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Store token in localStorage
                    localStorage.setItem('access_token', data.access_token);
                    
                    // Log para depuração
                    console.log("Token armazenado:", data.access_token);
                    
                    // Adicionar o token ao cabeçalho da próxima requisição
                    const headers = new Headers();
                    headers.append('Authorization', `Bearer ${data.access_token}`);
                    
                    // Redirecionar para o painel admin com o token no cabeçalho
                    fetch('/admin', {
                        method: 'GET',
                        headers: headers
                    }).then(response => {
                        if (response.ok) {
                            window.location.href = '/admin';
                        } else {
                            console.error('Erro ao acessar /admin:', response.status);
                            alert('Erro ao acessar o painel admin. Status: ' + response.status);
                        }
                    }).catch(error => {
                        console.error('Erro na requisição para /admin:', error);
                        alert('Erro ao acessar o painel admin.');
                    });
                } else {
                    const errorData = await response.json();
                    alert('Login failed: ' + (errorData.detail || 'Unknown error'));
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Login failed. Please try again.');
            }
        });
    }
});