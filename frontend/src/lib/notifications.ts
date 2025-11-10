import { create } from "zustand";

export type NotificationItem = {
  id: string;
  title: string;
  message: string;
  createdAt: string;
  read: boolean;
};

type NotificationState = {
  items: NotificationItem[];
  unreadCount: number;
  push: (notification: Omit<NotificationItem, "id" | "createdAt"> & { id?: string }) => void;
  markAllRead: () => void;
};

function buildNotification(payload: Omit<NotificationItem, "id" | "createdAt"> & { id?: string }): NotificationItem {
  const id =
    payload.id ??
    (typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`);
  return {
    id,
    title: payload.title,
    message: payload.message,
    read: payload.read ?? false,
    createdAt: new Date().toISOString(),
  };
}

const initializer = (
  set: (partial: NotificationState | ((state: NotificationState) => NotificationState)) => void,
) => ({
  items: [
    {
      id: "welcome",
      title: "Welcome to Wazifni",
      message: "Stay tuned for automation updates and application insights here.",
      createdAt: new Date().toISOString(),
      read: false,
    },
  ],
  unreadCount: 1,
  push: (notification: Omit<NotificationItem, "id" | "createdAt"> & { id?: string }) =>
    set((state: NotificationState) => {
      const item = buildNotification(notification);
      const items = [item, ...state.items].slice(0, 20);
      const unreadCount = items.filter((entry) => !entry.read).length;
      return { ...state, items, unreadCount };
    }),
  markAllRead: () =>
    set((state: NotificationState) => ({
      ...state,
      items: state.items.map((item) => ({ ...item, read: true })),
      unreadCount: 0,
    })),
});

export const useNotifications = create<NotificationState>(initializer);
