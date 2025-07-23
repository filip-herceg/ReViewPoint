/**
 * ESLint Rules for Button Standards
 * Add these rules to your .eslintrc.js to enforce Button component usage
 */

module.exports = {
	rules: {
		// Prevent raw button elements
		"no-restricted-syntax": [
			"error",
			{
				selector: 'JSXElement[openingElement.name.name="button"]',
				message:
					"Use the Button component from @/components/ui/button instead of raw <button> elements. See BUTTON_STANDARDS.md for guidelines.",
			},
		],

		// Prevent style prop on Button components (use variants instead)
		"react/no-unknown-property": [
			"error",
			{
				ignore: ["data-*", "aria-*"],
				// Custom rule to warn about style prop on Button
			},
		],
	},

	// Add custom rule for multiple children in Button asChild
	overrides: [
		{
			files: ["**/*.tsx", "**/*.ts"],
			rules: {
				"button-aschild-single-child": "error",
			},
		},
	],
};

// Custom ESLint rule implementation (add to eslint-plugin-local or similar)
const buttonAsChildRule = {
	meta: {
		type: "problem",
		docs: {
			description:
				"Button with asChild prop must have exactly one child element",
			category: "Possible Errors",
			recommended: true,
		},
		messages: {
			multipleChildren:
				"Button with asChild prop must have exactly one child element. Wrap multiple elements in a single container.",
			noChildren:
				"Button with asChild prop must have exactly one child element.",
		},
	},

	create(context) {
		return {
			JSXElement(node) {
				if (
					node.openingElement.name.name === "Button" &&
					node.openingElement.attributes.some(
						(attr) => attr.name && attr.name.name === "asChild",
					)
				) {
					const children = node.children.filter(
						(child) =>
							child.type === "JSXElement" ||
							(child.type === "JSXText" && child.value.trim()),
					);

					if (children.length === 0) {
						context.report({
							node,
							messageId: "noChildren",
						});
					} else if (children.length > 1) {
						context.report({
							node,
							messageId: "multipleChildren",
						});
					}
				}
			},
		};
	},
};

module.exports.buttonAsChildRule = buttonAsChildRule;
