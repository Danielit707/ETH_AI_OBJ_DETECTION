"use client";

interface Props {
  status: "checking" | "online" | "offline";
}

const STATUS_CONFIG = {
  checking: { color: "bg-yellow-500", text: "yellow", label: "Checking API..." },
  online: { color: "bg-green-500", text: "green", label: "API Online" },
  offline: { color: "bg-red-500", text: "red", label: "API Offline" },
};

export default function ApiStatus({ status }: Props) {
  const config = STATUS_CONFIG[status];
  return (
    <div className="flex items-center gap-2 rounded-full bg-surface-light px-4 py-1.5">
      <span className="relative flex h-2.5 w-2.5">
        <span
          className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-60 ${config.color}`}
        />
        <span
          className={`relative inline-flex h-2.5 w-2.5 rounded-full ${config.color}`}
        />
      </span>
      <span className={`text-sm font-medium text-${config.text}-400`}>
        {config.label}
      </span>
    </div>
  );
}
