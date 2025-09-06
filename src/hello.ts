/**
 * Returns a simple greeting message.
 * @param name - Optional name to include in the greeting
 * @returns A simple greeting string
 */
export const hello = (name?: string): string => {
  if (!name) {
    return 'hi';
  }
  return `hi, ${name}`;
};
