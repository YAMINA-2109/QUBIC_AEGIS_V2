import * as React from "react"
import { cn } from "../../lib/utils"

const badgeVariants = {
  base: "inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 transition-colors overflow-hidden",
  variants: {
    default: "border-transparent bg-primary text-primary-foreground",
    secondary:
      "border-transparent bg-secondary text-secondary-foreground",
    destructive:
      "border-transparent bg-destructive text-white",
    outline: "text-foreground",
  },
}

interface BadgeProps extends React.ComponentProps<"span"> {
  variant?: keyof typeof badgeVariants.variants
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        badgeVariants.base,
        badgeVariants.variants[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }

