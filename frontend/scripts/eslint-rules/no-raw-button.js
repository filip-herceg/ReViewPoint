/**
 * Custom ESLint rule to enforce Button component usage instead of raw <button> elements
 * This ensures consistency and prevents bypassing the standardized button system
 */

const rule = {
	meta: {
		type: "problem",
		docs: {
			description:
				"Enforce use of standardized Button component instead of raw <button> elements",
			category: "Best Practices",
			recommended: true,
		},
		fixable: null,
		schema: [],
		messages: {
			noRawButton:
				"Use the standardized Button component from @/components/ui/button instead of raw <button> elements. See docs/development/BUTTON_STANDARDS.md for guidance.",
		},
	},

	create(context) {
		return {
			JSXOpeningElement(node) {
				if (node.name && node.name.name === "button") {
					// Allow <button> if it's inside a Button component implementation
					const _sourceCode = context.getSourceCode();
					const filename = context.getFilename();

					// Skip the rule for the Button component itself
					if (
						filename.includes("/components/ui/button.tsx") ||
						filename.includes("\\components\\ui\\button.tsx")
					) {
						return;
					}

					context.report({
						node,
						messageId: "noRawButton",
					});
				}
			},
		};
	},
};

export default rule;
