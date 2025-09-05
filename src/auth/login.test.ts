/**
 * Tests for authentication login functionality
 */

import { AuthService, LoginCredentials } from './login';

describe('AuthService', () => {
  let authService: AuthService;
  
  beforeEach(() => {
    authService = new AuthService();
  });
  
  describe('login', () => {
    it('should authenticate valid credentials', async () => {
      const credentials: LoginCredentials = {
        username: 'testuser',
        password: 'testpass'
      };
      
      const result = await authService.login(credentials);
      
      expect(result.success).toBe(true);
      expect(result.token).toBeDefined();
    });
    
    it('should reject empty credentials', async () => {
      const credentials: LoginCredentials = {
        username: '',
        password: ''
      };
      
      const result = await authService.login(credentials);
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('required');
    });
  });
  
  describe('validateToken', () => {
    it('should validate non-empty tokens', async () => {
      const result = await authService.validateToken('valid-token');
      expect(result).toBe(true);
    });
    
    it('should reject empty tokens', async () => {
      const result = await authService.validateToken('');
      expect(result).toBe(false);
    });
  });
});
