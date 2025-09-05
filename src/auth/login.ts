/**
 * User authentication service
 * Implements secure login functionality
 */

import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

interface User {
  id: string;
  email: string;
  passwordHash: string;
  firstName?: string;
  lastName?: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  user: Omit<User, 'passwordHash'>;
  token: string;
}

export class AuthService {
  private jwtSecret: string;
  private jwtExpiresIn: string;

  constructor() {
    this.jwtSecret = process.env.JWT_SECRET || 'default-secret';
    this.jwtExpiresIn = process.env.JWT_EXPIRES_IN || '24h';
  }

  /**
   * Authenticate user with email and password
   * @param credentials User login credentials
   * @returns User data and JWT token
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // Validate input
    if (!credentials.email || !credentials.password) {
      throw new Error('Email and password are required');
    }

    // Find user by email (mock implementation)
    const user = await this.findUserByEmail(credentials.email);
    if (!user) {
      throw new Error('Invalid credentials');
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(credentials.password, user.passwordHash);
    if (!isValidPassword) {
      throw new Error('Invalid credentials');
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      this.jwtSecret,
      { expiresIn: this.jwtExpiresIn } as jwt.SignOptions
    );

    // Return user data without password hash
    const { passwordHash, ...userWithoutPassword } = user;
    return {
      user: userWithoutPassword,
      token
    };
  }

  /**
   * Find user by email address
   * @param email User email address
   * @returns User object or null if not found
   */
  private async findUserByEmail(email: string): Promise<User | null> {
    // Mock implementation - replace with actual database query
    return {
      id: '1',
      email: email,
      passwordHash: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.5.6.7.8.9.0',
      firstName: 'John',
      lastName: 'Doe'
    };
  }
}