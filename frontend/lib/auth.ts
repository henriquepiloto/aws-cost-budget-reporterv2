import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { query } from './db';

const JWT_SECRET = process.env.JWT_SECRET || 'cloudinho-secret-key-2024';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  created_at: string;
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);
}

export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword);
}

export function generateToken(user: User): string {
  return jwt.sign(
    { 
      id: user.id, 
      username: user.username, 
      role: user.role 
    },
    JWT_SECRET,
    { expiresIn: '24h' }
  );
}

export function verifyToken(token: string): any {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
}

export async function authenticateUser(username: string, password: string): Promise<User | null> {
  try {
    const users = await query(
      'SELECT * FROM users WHERE username = ? OR email = ?',
      [username, username]
    ) as any[];

    if (users.length === 0) {
      return null;
    }

    const user = users[0];
    const isValid = await verifyPassword(password, user.password);

    if (!isValid) {
      return null;
    }

    // Log access
    await query(
      'INSERT INTO user_logs (user_id, action, ip_address, created_at) VALUES (?, ?, ?, NOW())',
      [user.id, 'login', 'system']
    );

    return {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
      created_at: user.created_at
    };
  } catch (error) {
    console.error('Authentication error:', error);
    return null;
  }
}
