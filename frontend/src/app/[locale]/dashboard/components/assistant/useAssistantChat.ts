"use client";

import { startTransition, useEffect, useMemo, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiPostStreamAuthorized } from "@/lib/api";
import { useAuth } from "@/lib/store";

export type AssistantRole = "user" | "assistant";

export interface AssistantMessage {
  id: string;
  role: AssistantRole;
  content: string;
  createdAt: string;
  streaming?: boolean;
  error?: boolean;
}

export interface AssistantContext {
  locale: string;
  profileId?: string | number | null;
  jobId?: string | number | null;
}

interface MutationVariables {
  prompt: string;
  assistantId: string;
  history: Array<{ role: AssistantRole; content: string }>;
  context?: AssistantContext;
}

interface MutationResult {
  assistantId: string;
  text: string;
}

const STORAGE_NAMESPACE = "wazifni.assistant.v1";
const MAX_HISTORY = 40;

function generateId(prefix: string): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${prefix}-${Math.random().toString(36).slice(2, 12)}`;
}

function getStorageKey(userId?: string | number | null): string {
  const suffix = userId ?? "guest";
  return `${STORAGE_NAMESPACE}.${suffix}`;
}

function loadHistory(key: string): AssistantMessage[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed
      .map((item) => {
        if (!item || typeof item !== "object") {
          return null;
        }
        const role = (item as Record<string, unknown>).role;
        const content = (item as Record<string, unknown>).content;
        const createdAt = (item as Record<string, unknown>).createdAt;
        if ((role === "user" || role === "assistant") && typeof content === "string") {
          return {
            id: typeof (item as Record<string, unknown>).id === "string"
              ? ((item as Record<string, unknown>).id as string)
              : generateId("restored"),
            role,
            content,
            createdAt: typeof createdAt === "string" ? createdAt : new Date().toISOString(),
          } satisfies AssistantMessage;
        }
        return null;
      })
      .filter((entry): entry is AssistantMessage => Boolean(entry))
      .slice(-MAX_HISTORY);
  } catch {
    return [];
  }
}

function historiesEqual(a: AssistantMessage[], b: AssistantMessage[]): boolean {
  if (a.length !== b.length) {
    return false;
  }
  for (let index = 0; index < a.length; index += 1) {
    const left = a[index];
    const right = b[index];
    if (
      left.id !== right.id ||
      left.role !== right.role ||
      left.content !== right.content ||
      left.streaming !== right.streaming ||
      left.error !== right.error
    ) {
      return false;
    }
  }
  return true;
}

export function useAssistantChat() {
  const { token, user } = useAuth();
  const storageKey = useMemo(() => getStorageKey(user?.id ?? user?.email ?? "guest"), [user?.email, user?.id]);
  const [messages, setMessages] = useState<AssistantMessage[]>(() => loadHistory(storageKey));
  const [error, setError] = useState<string | null>(null);

  const messagesRef = useRef(messages);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const history = loadHistory(storageKey);
    startTransition(() => {
      setMessages((prev) => (historiesEqual(prev, history) ? prev : history));
    });
  }, [storageKey]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const trimmed = messages.slice(-MAX_HISTORY);
    window.localStorage.setItem(storageKey, JSON.stringify(trimmed));
  }, [messages, storageKey]);

  const mutation = useMutation<MutationResult, Error, MutationVariables>({
    mutationFn: async (variables) => {
      if (!token) {
        throw new Error("API Error 401");
      }

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      let collected = "";

      const payload = {
        message: variables.prompt,
        history: variables.history,
        locale: variables.context?.locale,
        profile_id: variables.context?.profileId ?? null,
        job_id: variables.context?.jobId ?? null,
      };

      const result = await apiPostStreamAuthorized<{ reply?: string }>(
        "/assistant/respond",
        payload,
        token,
        {
          signal: controller.signal,
          onChunk: (chunk) => {
            collected += chunk;
            setMessages((prev) =>
              prev.map((message) =>
                message.id === variables.assistantId
                  ? {
                      ...message,
                      content: (message.content ?? "") + chunk,
                    }
                  : message
              )
            );
          },
        }
      );

      if (!collected) {
        const parsed = result.parsed;
        if (parsed && typeof parsed === "object" && parsed !== null && "reply" in parsed) {
          const reply = (parsed as Record<string, unknown>).reply;
          if (typeof reply === "string") {
            collected = reply;
          }
        }
        if (!collected && result.fullText) {
          collected = result.fullText;
        }
        if (collected) {
          const content = collected;
          setMessages((prev) =>
            prev.map((message) =>
              message.id === variables.assistantId
                ? {
                    ...message,
                    content,
                  }
                : message
            )
          );
        }
      }

      return {
        assistantId: variables.assistantId,
        text: collected,
      } satisfies MutationResult;
    },
    onSuccess: (data) => {
      setError(null);
      setMessages((prev) =>
        prev.map((message) =>
          message.id === data.assistantId
            ? {
                ...message,
                streaming: false,
                error: false,
              }
            : message
        )
      );
    },
    onError: (err, variables) => {
      setError(err.message);
      setMessages((prev) =>
        prev.map((message) =>
          message.id === variables.assistantId
            ? {
                ...message,
                streaming: false,
                error: true,
              }
            : message
        )
      );
    },
    onSettled: () => {
      abortRef.current = null;
    },
  });

  const sendMessage = (prompt: string, context?: AssistantContext): boolean => {
    const trimmed = prompt.trim();
    if (!trimmed) {
      return false;
    }

    if (!token) {
      setError("API Error 401");
      return false;
    }

    if (mutation.isPending) {
      return false;
    }

    setError(null);

    const userMessage: AssistantMessage = {
      id: generateId("user"),
      role: "user",
      content: trimmed,
      createdAt: new Date().toISOString(),
    };

    const assistantId = generateId("assistant");
    const assistantMessage: AssistantMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
      streaming: true,
    };

    const history = [...messagesRef.current, userMessage].map(({ role, content }) => ({
      role,
      content,
    }));

    setMessages((prev) => {
      const next = [...prev, userMessage, assistantMessage];
      if (next.length > MAX_HISTORY) {
        return next.slice(-MAX_HISTORY);
      }
      return next;
    });

    mutation.mutate({
      prompt: trimmed,
      assistantId,
      history,
      context,
    });

    return true;
  };

  const clearHistory = () => {
    abortRef.current?.abort();
    abortRef.current = null;
    setError(null);
    setMessages([]);
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(storageKey);
    }
  };

  const cancelReply = () => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setMessages((prev) =>
      prev.map((message) =>
        message.streaming
          ? {
              ...message,
              streaming: false,
            }
          : message
      )
    );
  };

  return {
    messages,
    sendMessage,
    clearHistory,
    cancelReply,
    error,
    isStreaming: mutation.isPending || messages.some((message) => message.streaming),
    isSending: mutation.isPending,
  } as const;
}
