// src/components/ui/card.jsx
import clsx from "clsx";

/* Root container — usually wraps <CardHeader>, <CardContent>, etc. */
export function Card({ className, children, ...props }) {
  return (
    <div
      className={clsx(
        "rounded-2xl border border-slate-200 bg-white shadow-sm",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

/* Optional header row (title / description) */
export function CardHeader({ className, children, ...props }) {
  return (
    <div className={clsx("p-6 pb-0", className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className, children, ...props }) {
  return (
    <h3
      className={clsx(
        "font-serif text-xl font-semibold text-slate-900",
        className
      )}
      {...props}
    >
      {children}
    </h3>
  );
}

export function CardDescription({ className, children, ...props }) {
  return (
    <p
      className={clsx("mt-1 text-base leading-relaxed text-slate-700", className)}
      {...props}
    >
      {children}
    </p>
  );
}

/* Main body — what you’re using in GuidanceSection */
export function CardContent({ className, children, ...props }) {
  return (
    <div className={clsx("p-6", className)} {...props}>
      {children}
    </div>
  );
}

/* Optional footer row (buttons, links, etc.) */
export function CardFooter({ className, children, ...props }) {
  return (
    <div className={clsx("p-6 pt-0", className)} {...props}>
      {children}
    </div>
  );
}
