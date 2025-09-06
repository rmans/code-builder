/**
 * Returns a personalized greeting message.
 * @param name - Optional name to include in the greeting
 * @returns A friendly greeting string
 * @example
 * ```typescript
 * hello("Alice") // returns "Hello, Alice!"
 * hello() // returns "Hello, World!"
 * ```
 */
export const hello = (name?: string): string => {
  if (!name || name.trim() === '') {
    return 'Hello, World!';
  }
  return `Hello, ${name.trim()}!`;
};

/**
 * Validates that a name is acceptable for greetings
 * @param name - The name to validate
 * @returns True if the name is valid, false otherwise
 */
export const isValidName = (name: string): boolean => {
  return name.length > 0 && name.length <= 50 && /^[a-zA-Z\s-']+$/.test(name);
};

/**
 * Creates a formal greeting with title
 * @param name - The person's name
 * @param title - Optional title (Mr., Ms., Dr., etc.)
 * @returns A formal greeting string
 */
export const formalGreeting = (name: string, title?: string): string => {
  if (!isValidName(name)) {
    throw new Error('Invalid name provided');
  }
  
  const prefix = title ? `${title} ` : '';
  return `Good day, ${prefix}${name}.`;
};
