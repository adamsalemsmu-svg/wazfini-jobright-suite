"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useAssistantChat } from "./useAssistantChat";

interface AssistantPanelProps {
  profileId?: string | number | null;
  jobId?: string | number | null;
}

const MAX_INPUT_LENGTH = 2000;

function formatTimestamp(value: string, locale: string): string {
  try {
    return new Intl.DateTimeFormat(locale, {
      hour: "numeric",
      minute: "numeric",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function mapErrorMessage(raw: string | null, translate: ReturnType<typeof useTranslations>): string | null {
  if (!raw) {
    return null;
  }
  if (raw.includes("401")) {
    return translate("errors.unauthorized");
  }
  if (raw.includes("AbortError")) {
    return translate("errors.cancelled");
  }
  return translate("errors.generic");
}

export function AssistantPanel({ profileId, jobId }: AssistantPanelProps) {
  const t = useTranslations("Dashboard.assistant");
  const locale = useLocale();
  const { messages, sendMessage, clearHistory, cancelReply, error, isStreaming, isSending } = useAssistantChat();
  const [input, setInput] = useState("");
  const [open, setOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    setErrorMessage(mapErrorMessage(error, t));
  }, [error, t]);

  useEffect(() => {
    if (!open) {
      return;
    }
    const lastElement = messagesEndRef.current;
    if (lastElement) {
      lastElement.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [messages, open]);

  const handleSubmit = () => {
    const successful = sendMessage(input, { locale, profileId, jobId });
    if (successful) {
      setInput("");
      setErrorMessage(null);
    } else if (!errorMessage) {
      setErrorMessage(t("errors.generic"));
    }
  };

  const handleClearHistory = () => {
    if (window.confirm(t("confirmClear"))) {
      clearHistory();
      setErrorMessage(null);
    }
  };

  const remaining = useMemo(() => MAX_INPUT_LENGTH - input.length, [input.length]);

  return (
    <Card className="flex flex-col overflow-hidden">
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <div>
          <CardTitle>{t("title")}</CardTitle>
          <CardDescription>{t("subtitle")}</CardDescription>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setOpen((prev) => !prev)}>
          {open ? t("toggle.close") : t("toggle.open")}
        </Button>
      </CardHeader>

      {open ? (
        <CardContent className="flex h-[480px] flex-col gap-4">
          {errorMessage ? (
            <Alert variant="destructive">
              <AlertDescription className="flex items-center justify-between gap-3">
                <span>{errorMessage}</span>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 px-3 text-xs"
                  onClick={() => setErrorMessage(null)}
                >
                  {t("dismiss")}
                </Button>
              </AlertDescription>
            </Alert>
          ) : null}

          <div
            className="flex-1 space-y-3 overflow-y-auto pr-1"
            dir={locale === "ar" ? "rtl" : "ltr"}
          >
            {messages.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("empty")}</p>
            ) : (
              messages.map((message) => {
                const isUser = message.role === "user";
                const bubbleClass = cn(
                  "max-w-[90%] rounded-2xl px-3 py-2 text-sm shadow-sm",
                  isUser
                    ? "ml-auto bg-primary text-primary-foreground"
                    : "mr-auto border bg-muted/60 text-foreground"
                );
                const metaClass = cn(
                  "mt-1 text-xs text-muted-foreground",
                  isUser ? "text-right" : "text-left"
                );
                const displayContent = message.content.trim().length
                  ? message.content
                  : message.streaming
                    ? t("typing")
                    : "";

                return (
                  <div key={message.id} className="flex flex-col">
                    <div className={bubbleClass}>
                      <p className="whitespace-pre-wrap break-words leading-relaxed">
                        {displayContent}
                        {message.streaming ? (
                          <span className="ml-1 inline-flex h-2 w-2 animate-pulse rounded-full bg-current align-middle" />
                        ) : null}
                        {message.error ? (
                          <span className="ml-2 text-xs font-medium text-destructive">
                            {t("errors.short")}
                          </span>
                        ) : null}
                      </p>
                    </div>
                    <span className={metaClass}>{formatTimestamp(message.createdAt, locale)}</span>
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>

          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              handleSubmit();
            }}
          >
            <Textarea
              value={input}
              onChange={(event) => {
                if (event.target.value.length <= MAX_INPUT_LENGTH) {
                  setInput(event.target.value);
                }
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  handleSubmit();
                }
              }}
              placeholder={t("placeholder")}
              rows={4}
              dir={locale === "ar" ? "rtl" : "ltr"}
            />
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
              <span>{t("charCount", { value: remaining })}</span>
              <div className="flex items-center gap-2">
                {isStreaming ? (
                  <Button variant="ghost" size="sm" type="button" onClick={cancelReply}>
                    {t("cancel")}
                  </Button>
                ) : null}
                <Button
                  variant="outline"
                  size="sm"
                  type="button"
                  onClick={handleClearHistory}
                  disabled={messages.length === 0}
                >
                  {t("clear")}
                </Button>
                <Button type="submit" size="sm" disabled={!input.trim() || isSending}>
                  {isSending ? t("sending") : t("send")}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      ) : null}
    </Card>
  );
}
