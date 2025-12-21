import { defineConfig } from 'vitest/config';


export default defineConfig({
    test: {
        globals: true,
        environment: 'node',    // 'jsdom' can be used if DOM APIs are needed -> UI 테스트까지 할지 생각중임
        setupFiles: ['./vitest.setup.ts'],
        include: ["src/**/*.{test,spec}.ts", "src/**/*.{test,spec}.tsx"],
    }
});