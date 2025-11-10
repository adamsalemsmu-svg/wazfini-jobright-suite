"use client";

import { useState } from "react";
import { Bell } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useNotifications, type NotificationItem } from "@/lib/notifications";

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const { items, unreadCount, markAllRead } = useNotifications();

  const toggle = () => {
    setOpen((value: boolean) => {
      const next = !value;
      if (next === false) {
        markAllRead();
      }
      return next;
    });
  };

  return (
    <div className="relative">
      <Button
        variant={unreadCount ? "default" : "outline"}
        size="icon"
        onClick={toggle}
        aria-label="Notifications"
      >
        <Bell className="h-4 w-4" />
        {unreadCount ? (
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-semibold text-destructive-foreground">
            {unreadCount}
          </span>
        ) : null}
      </Button>
      {open ? (
        <div className="absolute right-0 z-20 mt-2 w-72 rounded-md border bg-background p-3 shadow-lg">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold">Notifications</p>
            {unreadCount ? (
              <button
                type="button"
                className="text-xs font-medium text-primary underline-offset-4 hover:underline"
                onClick={markAllRead}
              >
                Mark read
              </button>
            ) : null}
          </div>
          <div className="mt-2 space-y-2">
            {items.length === 0 ? (
              <p className="text-sm text-muted-foreground">All caught up!</p>
            ) : (
              items.map((item: NotificationItem) => (
                <div
                  key={item.id}
                  className="rounded-md border border-border bg-muted/40 p-2"
                >
                  <p className="text-sm font-medium">{item.title}</p>
                  <p className="text-xs text-muted-foreground">{item.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
