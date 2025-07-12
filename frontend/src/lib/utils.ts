import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import logger from "@/logger";

export function cn(...inputs: ClassValue[]): string {
	try {
		const clsxResult = clsx(inputs);
		const merged = twMerge(clsxResult);
		logger.debug("Class names merged successfully", { inputs, merged });
		return merged || "";
	} catch (err) {
		logger.error("Error merging class names", { error: err });
		return "error error-class-merge";
	}
}
