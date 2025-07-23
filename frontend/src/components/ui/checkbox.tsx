import { Check } from "lucide-react";
import * as React from "react";
import { cn } from "@/lib/utils";

interface CheckboxProps
  extends Omit<
    React.InputHTMLAttributes<HTMLInputElement>,
    "onChange" | "type"
  > {
  onCheckedChange?: (checked: boolean) => void;
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, onCheckedChange, checked, ...props }, ref) => {
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      onCheckedChange?.(event.target.checked);
    };

    return (
      <div className="relative">
        <input
          type="checkbox"
          ref={ref}
          className={cn(
            "peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none bg-background",
            "data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground",
            "checked:bg-primary checked:border-primary",
            className,
          )}
          checked={checked}
          onChange={handleChange}
          {...props}
        />
        {checked && (
          <Check className="absolute top-0 left-0 h-4 w-4 text-primary-foreground pointer-events-none" />
        )}
      </div>
    );
  },
);

Checkbox.displayName = "Checkbox";

export { Checkbox };
