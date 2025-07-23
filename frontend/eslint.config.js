import js from "@eslint/js";
import typescript from "@typescript-eslint/eslint-plugin";
import typescriptParser from "@typescript-eslint/parser";
import jsxA11y from "eslint-plugin-jsx-a11y";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import noRawButton from "./scripts/eslint-rules/no-raw-button.js";

export default [
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: "module",
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        // Browser globals
        window: "readonly",
        document: "readonly",
        console: "readonly",
        process: "readonly",
        navigator: "readonly",
        localStorage: "readonly",
        sessionStorage: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        alert: "readonly",
        confirm: "readonly",
        prompt: "readonly",
        fetch: "readonly",
        URL: "readonly",
        URLSearchParams: "readonly",
        Blob: "readonly",
        File: "readonly",
        FileList: "readonly",
        FileReader: "readonly",
        FormData: "readonly",
        Headers: "readonly",
        Request: "readonly",
        Response: "readonly",
        AbortController: "readonly",
        AbortSignal: "readonly",
        ReadableStream: "readonly",
        WritableStream: "readonly",
        crypto: "readonly",
        btoa: "readonly",
        atob: "readonly",
        performance: "readonly",

        // HTML Element types
        HTMLElement: "readonly",
        HTMLDivElement: "readonly",
        HTMLButtonElement: "readonly",
        HTMLInputElement: "readonly",
        HTMLTextAreaElement: "readonly",
        HTMLSelectElement: "readonly",
        HTMLFormElement: "readonly",
        HTMLImageElement: "readonly",
        HTMLAnchorElement: "readonly",
        HTMLParagraphElement: "readonly",
        HTMLHeadingElement: "readonly",
        HTMLCanvasElement: "readonly",
        HTMLVideoElement: "readonly",
        HTMLAudioElement: "readonly",
        SVGElement: "readonly",
        SVGSVGElement: "readonly",

        // Event types
        Event: "readonly",
        MouseEvent: "readonly",
        KeyboardEvent: "readonly",
        TouchEvent: "readonly",
        FocusEvent: "readonly",
        ChangeEvent: "readonly",
        FormEvent: "readonly",
        DragEvent: "readonly",

        // Other browser types
        NodeJS: "readonly",
        React: "readonly",
        Console: "readonly",

        // Node.js globals (for build scripts)
        __dirname: "readonly",
        __filename: "readonly",
        global: "readonly",
        module: "readonly",
        require: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": typescript,
      "react-hooks": reactHooks,
      "jsx-a11y": jsxA11y,
      react: react,
      custom: {
        rules: {
          "no-raw-button": noRawButton,
        },
      },
    },
    rules: {
      ...typescript.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      ...jsxA11y.configs.recommended.rules,
      "custom/no-raw-button": "error",
      // Additional rules
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          destructuredArrayIgnorePattern: "^_",
        },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/explicit-module-boundary-types": "off",
      "@typescript-eslint/no-empty-function": "off",
      "@typescript-eslint/no-require-imports": "warn",
      "react/react-in-jsx-scope": "off",
      "no-redeclare": "error",
      "no-empty": "error",
      "jsx-a11y/heading-has-content": ["error", { components: [""] }],
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
  // Test files configuration
  {
    files: [
      "**/*.test.{js,jsx,ts,tsx}",
      "**/*.spec.{js,jsx,ts,tsx}",
      "**/tests/**/*.{js,jsx,ts,tsx}",
      "**/e2e/**/*.{js,jsx,ts,tsx}",
    ],
    languageOptions: {
      globals: {
        // Vitest globals
        describe: "readonly",
        it: "readonly",
        test: "readonly",
        expect: "readonly",
        beforeAll: "readonly",
        afterAll: "readonly",
        beforeEach: "readonly",
        afterEach: "readonly",
        vi: "readonly",
        // Jest globals (if used)
        jest: "readonly",
        // Playwright globals
        page: "readonly",
      },
    },
    rules: {
      "@typescript-eslint/no-explicit-any": "off", // Allow any in tests
      "@typescript-eslint/no-unused-vars": "off", // More lenient in tests
    },
  },
  // Mock files configuration
  {
    files: [
      "**/__mocks__/**/*.{js,jsx,ts,tsx}",
      "**/mocks/**/*.{js,jsx,ts,tsx}",
    ],
    languageOptions: {
      globals: {
        jest: "readonly",
        vi: "readonly",
      },
    },
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
    },
  },
  // Build and config files
  {
    files: [
      "**/*.config.{js,ts}",
      "**/*.setup.{js,ts}",
      "**/scripts/**/*.{js,ts}",
    ],
    rules: {
      "@typescript-eslint/no-require-imports": "off",
      "no-undef": "off", // These files may use Node.js requires
    },
  },
  {
    ignores: [
      "dist/**",
      "node_modules/**",
      ".eslintrc.cjs",
      "vite.config.ts",
      "build/**",
      "coverage/**",
    ],
  },
];
