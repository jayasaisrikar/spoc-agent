/**
 * User management utility functions
 */

class UserManager {
    constructor() {
        this.apiBase = '/api';
    }

    async createUser(username, email) {
        try {
            const response = await fetch(`${this.apiBase}/users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email })
            });
            return await response.json();
        } catch (error) {
            console.error('Error creating user:', error);
            return { success: false, message: 'Network error' };
        }
    }

    async getUsers() {
        try {
            const response = await fetch(`${this.apiBase}/users`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching users:', error);
            return { users: [] };
        }
    }

    renderUserList(users) {
        const container = document.getElementById('userList');
        if (!container) return;

        container.innerHTML = users.map(user => `
            <div class="user-card">
                <h3>${user[1]}</h3>
                <p>Email: ${user[2]}</p>
                <small>Created: ${user[3]}</small>
            </div>
        `).join('');
    }

    setupEventListeners() {
        const form = document.getElementById('userForm');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const result = await this.createUser(
                    formData.get('username'),
                    formData.get('email')
                );
                
                if (result.success) {
                    form.reset();
                    this.loadUsers();
                } else {
                    alert(result.message);
                }
            });
        }
    }

    async loadUsers() {
        const result = await this.getUsers();
        this.renderUserList(result.users);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const userManager = new UserManager();
    userManager.setupEventListeners();
    userManager.loadUsers();
});
