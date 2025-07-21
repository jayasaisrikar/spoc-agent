/**
 * Database models and schemas
 */

const DatabaseSchema = {
    users: {
        id: 'INTEGER PRIMARY KEY',
        username: 'TEXT UNIQUE NOT NULL',
        email: 'TEXT NOT NULL',
        created_at: 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    },
    
    sessions: {
        id: 'INTEGER PRIMARY KEY',
        user_id: 'INTEGER',
        token: 'TEXT UNIQUE',
        expires_at: 'TIMESTAMP',
        created_at: 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    }
};

class User {
    constructor(id, username, email, created_at) {
        this.id = id;
        this.username = username;
        this.email = email;
        this.created_at = created_at;
    }

    static validate(userData) {
        const errors = [];
        
        if (!userData.username || userData.username.length < 3) {
            errors.push('Username must be at least 3 characters long');
        }
        
        if (!userData.email || !this.isValidEmail(userData.email)) {
            errors.push('Valid email is required');
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    toJSON() {
        return {
            id: this.id,
            username: this.username,
            email: this.email,
            created_at: this.created_at
        };
    }
}

class Session {
    constructor(id, user_id, token, expires_at, created_at) {
        this.id = id;
        this.user_id = user_id;
        this.token = token;
        this.expires_at = expires_at;
        this.created_at = created_at;
    }

    isExpired() {
        return new Date() > new Date(this.expires_at);
    }

    static generateToken() {
        return Math.random().toString(36).substr(2) + Date.now().toString(36);
    }
}

module.exports = {
    DatabaseSchema,
    User,
    Session
};
