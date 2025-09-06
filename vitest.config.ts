import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['test/**/*.test.ts', 'tests/**/*.test.ts'],
    environment: 'node',
    globals: true,
    reporters: ['json', 'verbose'],
    outputFile: {
      json: 'builder/cache/vitest.json',
    },
    coverage: {
      reporter: ['json'],
      reportsDirectory: 'builder/cache',
    },
  },
});
