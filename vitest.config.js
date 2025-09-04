import { defineConfig } from 'vitest/config';
export default defineConfig({
    test: {
        include: ['test/**/*.test.ts'],
        environment: 'node',
        globals: true,
    },
});
//# sourceMappingURL=vitest.config.js.map