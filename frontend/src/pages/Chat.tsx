import { useState, useRef, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { ScrollArea } from "../components/ui/scroll-area";
import { apiUrl } from "../lib/api";
import {
  Bot,
  Send,
  Loader2,
  Shield,
  TrendingDown,
  BarChart3,
} from "lucide-react";
import { WalletGraph } from "../components/wallet-graph";
import { cn } from "../lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm AEGIS, your AI security copilot for Qubic blockchain. Ask me anything about network security, risk analysis, or transactions.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(apiUrl("api/ask-aegis"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          context: {},
        }),
      });

      const data = await response.json();

      // Better error handling for Groq issues
      let content =
        data.answer || "I apologize, but I couldn't generate a response.";
      if (
        !data.ai_generated &&
        data.answer?.includes("Groq API is not configured")
      ) {
        content =
          "Groq API is not configured. Please set GROQ_API_KEY in backend/.env file for full AI capabilities. Currently using fallback responses.";
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: content,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Error: ${error}. Please make sure the backend is running.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickAction = async (action: string) => {
    if (isLoading) return;

    const quickActions: Record<string, string> = {
      analyze: "Analyze the last security alert. What was detected and why?",
      whale:
        "Show me recent whale activity. Are there any suspicious large transactions?",
      predict:
        "Predict the risk level for the next 10 ticks. What should I watch for?",
    };

    const question = quickActions[action];
    if (!question) return;

    // Create user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(apiUrl("api/ask-aegis"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: question,
          context: {},
        }),
      });

      const data = await response.json();

      let content =
        data.answer || "I apologize, but I couldn't generate a response.";
      if (
        !data.ai_generated &&
        data.answer?.includes("Groq API is not configured")
      ) {
        content =
          "Groq API is not configured. Please set GROQ_API_KEY in backend/.env file for full AI capabilities. Currently using fallback responses.";
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: content,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Error: ${error}. Please make sure the backend is running.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight font-mono">
          ASK AEGIS - AI Security Copilot
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          Ask questions about network security, risk analysis, or transactions
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-primary/30">
          <CardHeader>
            <CardTitle className="text-sm font-mono uppercase text-muted-foreground flex items-center gap-2">
              <Bot className="h-4 w-4" />
              Chat with AEGIS
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col h-[calc(100vh-280px)]">
            <ScrollArea className="flex-1 mb-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <Bot className="h-5 w-5 text-primary mt-1 shrink-0" />
                    )}
                    <div
                      className={`rounded-lg px-4 py-2 max-w-[80%] ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-secondary text-secondary-foreground border border-primary/20"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">
                        {message.content}
                      </p>
                      <p className="text-xs opacity-60 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3 justify-start">
                    <Bot className="h-5 w-5 text-primary mt-1 shrink-0" />
                    <div className="bg-secondary rounded-lg px-4 py-2">
                      <Loader2 className="h-4 w-4 animate-spin text-primary" />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Quick Action Buttons */}
            <div className="mb-3 flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickAction("analyze")}
                disabled={isLoading}
                className="text-xs font-mono border-[#00ff41]/30 hover:bg-[#00ff41]/10 hover:border-[#00ff41]"
              >
                <Shield className="h-3 w-3 mr-1" />
                Analyze Last Alert
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickAction("whale")}
                disabled={isLoading}
                className="text-xs font-mono border-[#00ff41]/30 hover:bg-[#00ff41]/10 hover:border-[#00ff41]"
              >
                <TrendingDown className="h-3 w-3 mr-1" />
                Show Whale Activity
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleQuickAction("predict")}
                disabled={isLoading}
                className="text-xs font-mono border-[#00ff41]/30 hover:bg-[#00ff41]/10 hover:border-[#00ff41]"
              >
                <BarChart3 className="h-3 w-3 mr-1" />
                Predict Next Tick
              </Button>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask AEGIS about security, risks, or transactions..."
                className="flex-1 rounded-md border border-border bg-background px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={isLoading}
              />
              <Button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="bg-primary hover:bg-primary/90"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        <div>
          <WalletGraph maxNodes={30} />
        </div>
      </div>
    </div>
  );
}
