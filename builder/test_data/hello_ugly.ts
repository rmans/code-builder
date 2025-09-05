// This code works but is terrible quality
export const hello = (name?: string): string => {
  let x = name ? name : "World";
  let y = "Hello, " + x + "!";
  return y;
};

// Terrible variable names and structure
const a = (b: any) => {
  if (b) {
    if (b.length > 0) {
      if (b.length < 100) {
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  } else {
    return false;
  }
};

// Deeply nested and hard to read
export const processData = (data: any) => {
  if (data) {
    if (data.items) {
      if (data.items.length > 0) {
        if (data.items[0]) {
          if (data.items[0].value) {
            if (data.items[0].value > 0) {
              return data.items[0].value * 2;
            } else {
              return 0;
            }
          } else {
            return 0;
          }
        } else {
          return 0;
        }
      } else {
        return 0;
      }
    } else {
      return 0;
    }
  } else {
    return 0;
  }
};

// Magic numbers and unclear logic
export const calculate = (n: number) => {
  return n * 3.14159 + 42 - 17 * Math.random() * 0.5;
};
