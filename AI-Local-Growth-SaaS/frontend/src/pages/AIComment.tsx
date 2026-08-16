import { useState } from "react";
import * as aiApi from "../api/ai";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { toast } from "../utils/toast";

export default function AIComment() {
  const [video, setVideo] = useState("");
  const [industry, setIndustry] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [comments, setComments] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!video.trim()) {
      toast("请填写视频链接或描述", "error");
      return;
    }
    setSubmitting(true);
    try {
      const res = await aiApi.generateComment({ video: video.trim(), industry });
      setComments(res.comments);
    } catch {
      // toast by interceptor
    } finally {
      setSubmitting(false);
    }
  };

  const copy = (text: string) => {
    navigator.clipboard?.writeText(text).then(
      () => toast("已复制", "success"),
      () => toast("复制失败", "error")
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">AI 评论生成</h1>
        <p className="mt-1 text-sm text-slate-500">
          输入视频主题与行业，生成多条拟真语气评论（可复制）
        </p>
      </div>

      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle className="text-base">生成参数</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label>视频链接 / 描述 *</Label>
              <Textarea
                value={video}
                onChange={(e) => setVideo(e.target.value)}
                placeholder="粘贴视频号链接，或描述视频内容"
                rows={3}
              />
            </div>
            <div className="space-y-1.5">
              <Label>行业</Label>
              <Input
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="如：餐饮 / 美业 / 零售"
              />
            </div>
            <div className="flex justify-end">
              <Button type="submit" disabled={submitting}>
                {submitting ? "生成中…" : "生成评论"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {comments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">生成结果（{comments.length} 条）</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {comments.map((c, idx) => (
              <div
                key={idx}
                className="flex items-start justify-between gap-3 rounded-md border border-slate-200 p-3"
              >
                <p className="text-sm text-slate-700">{c}</p>
                <Button size="sm" variant="outline" onClick={() => copy(c)}>
                  复制
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
