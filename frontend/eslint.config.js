import { defineConfig } from "eslint-define-config";
import noRawButton from "./scripts/eslint-rules/no-raw-button.js";

export default defineConfig({
	root: true,
	env: {
		browser: true,
		es2020: true,
	},
	extends: [
		"eslint:recommended",
		"@typescript-eslint/recommended",
		"plugin:react-hooks/recommended",
		"plugin:jsx-a11y/recommended",
	],
	ignorePatterns: ["dist", ".eslintrc.cjs", "node_modules"],
	parser: "@typescript-eslint/parser",
	settings: {
		react: {
			version: "detect",
		},
	},
	// Register our custom rule
	plugins: {
		custom: {
			rules: {
				"no-raw-button": noRawButton,
			},
		},
	},
	rules: {
		...rules,
		"custom/no-raw-button": "error",
	},
});
