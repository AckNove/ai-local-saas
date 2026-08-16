import { useState } from "react";
import * as aiApi from "../api/ai";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select } from "../components/ui/select";
import { Textarea } from "../components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { toast } from "../utils/toast";

export default function AIContent() {
  const [type, setType] = useState<"script" | "copy">("script");
  const [industry, setIndustry] = useState("");
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [content, setContent] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      toast("请填写主题", "error");
      return;
    }
    setSubmitting(true);
    try {
      const res = await aiApi.generateContent({
        type,
        industry,
        topic: topic.trim(),
        tone: tone.trim() || null,
      });
      setContent(res.content);
    } catch {
      // toast by interceptor
    } finally {
      setSubmitting(false);
    }
  };

  const copy = () => {
    navigator.clipboard?.writeText(content).then(
      () => toast("已复制", "success"),
      () => toast("复制失败", "error")
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">AI 内容生成</h1>
        <p className="mt-1 text-sm text-slate-500">
          生成视频脚本或营销文案草稿（由商家手动发布，非自动发布）
        </p>
      </div>

      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle className="text-base">生成参数</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label>内容类型</Label>
              <Select value={type} onChange={(e) => setType(e.target.value as "script" | "copy")}>
                <option value="script">视频脚本</option>
                <option value="copy">营销文案</option>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>行业</Label>
              <Input
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="如：餐饮 / 美业 / 零售"
              />
            </div>
            <div className="space-y-1.5">
              <Label>主题 *</Label>
              <Input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="如：新店开业探店脚本"
              />
            </div>
            <div className="space-y-1.5">
              <Label>语气风格（可选）</Label>
              <Input
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                placeholder="如：活泼 / 专业 / 温情"
              />
            </div>
            <div className="flex justify-end">
              <Button type="submit" disabled={submitting}>
                {submitting ? "生成中…" : "生成内容"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {content && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">生成结果</CardTitle>
            <Button size="sm" variant="outline" onClick={copy}>
              复制
            </Button>
          </CardHeader>
          <CardContent>
            <Textarea readOnly value={content} rows={12} className="bg-slate-50" />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
