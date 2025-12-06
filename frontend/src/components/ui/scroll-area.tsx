import * as React from "react"
import { cn } from "../../lib/utils"

interface ScrollAreaProps extends React.ComponentProps<"div"> {
  children: React.ReactNode
}

function ScrollArea({ className, children, ...props }: ScrollAreaProps) {
  return (
    <div
      data-slot="scroll-area"
      className={cn("relative overflow-auto", className)}
      {...props}
    >
      <div className="size-full rounded-[inherit]">{children}</div>
    </div>
  )
}

export { ScrollArea }

