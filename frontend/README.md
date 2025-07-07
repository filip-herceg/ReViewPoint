# Frontend Development Setup

## Custom CSS At-Rules Support

This project uses custom CSS at-rules such as `@custom-variant` in `src/index.css`.

### How it works

- We use the [`@csstools/postcss-custom-variants`](https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-custom-variants) PostCSS plugin to process `@custom-variant`.
- The plugin is configured in `postcss.config.js` and installed as a dev dependency.
- This ensures all developers and CI builds process these at-rules identically.

### Requirements for all developers

- Run `pnpm install` after pulling changes to ensure you have all required plugins.
- Use the provided `postcss.config.js` and do not remove the custom plugin entry.
- For best editor experience, install the [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss) extension in VS Code.

### Troubleshooting

- If you see errors about unknown at-rules in your editor, make sure you have the IntelliSense extension and that your dependencies are up to date.
- If you add new custom at-rules, document and add the required PostCSS plugin in `postcss.config.js`.

---

For more details, see the main project [README](../README.md) or ask in the project chat.
