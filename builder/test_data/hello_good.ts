// Hello World TypeScript Example
// This is a simple TypeScript file for testing context generation

interface User {
  id: number;
  name: string;
  email: string;
}

class UserService {
  private users: User[] = [];

  addUser(user: User): void {
    this.users.push(user);
  }

  getUser(id: number): User | undefined {
    return this.users.find(user => user.id === id);
  }

  getAllUsers(): User[] {
    return [...this.users];
  }
}

export { User, UserService };
