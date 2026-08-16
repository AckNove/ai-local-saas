"""业务错误码与 BizError 异常。

错误码分段（与架构第 7 节一致）：
    0    成功
    1000 认证/授权
    2000 租户/资源
    3000 订单
    4000 核销
    5000 支付/退款
    6000 履约（自提/预约）
    9000 系统未知
"""
from __future__ import annotations

from enum import IntEnum


class ErrorCode(IntEnum):
    """统一业务错误码。"""

    # 认证 / 授权
    INVALID_TOKEN = 1001
    TOKEN_EXPIRED = 1002
    NO_PERMISSION = 1003

    # 租户 / 资源
    RESOURCE_NOT_FOUND = 2001
    CROSS_TENANT_DENIED = 2002
    RESOURCE_EXISTS = 2003

    # 订单
    ORDER_NOT_FOUND = 3001
    ORDER_STATUS_INVALID = 3002
    STOCK_NOT_ENOUGH = 3003
    PAY_TIMEOUT = 3004

    # 核销
    ALREADY_VERIFIED = 4001
    INVALID_VERIFY_CODE = 4002
    VERIFY_CODE_EXPIRED = 4003

    # 支付 / 退款
    PAY_FAILED = 5001
    REFUND_FAILED = 5002
    CHANNEL_ERROR = 5003

    # 履约（自提 / 预约）
    SLOT_FULL = 6001
    RESERVATION_NOT_FOUND = 6002
    RESERVATION_STATUS_INVALID = 6003

    # 系统
    SYSTEM_ERROR = 9000


# 错误码 -> 默认文案
_DEFAULT_MESSAGES: dict[int, str] = {
    ErrorCode.INVALID_TOKEN: "无效令牌",
    ErrorCode.TOKEN_EXPIRED: "令牌已过期",
    ErrorCode.NO_PERMISSION: "无权限",
    ErrorCode.RESOURCE_NOT_FOUND: "资源不存在",
    ErrorCode.CROSS_TENANT_DENIED: "跨租户访问被拒绝",
    ErrorCode.RESOURCE_EXISTS: "资源已存在",
    ErrorCode.ORDER_NOT_FOUND: "订单不存在",
    ErrorCode.ORDER_STATUS_INVALID: "订单状态非法",
    ErrorCode.STOCK_NOT_ENOUGH: "库存不足",
    ErrorCode.PAY_TIMEOUT: "支付超时",
    ErrorCode.ALREADY_VERIFIED: "该核销码已核销",
    ErrorCode.INVALID_VERIFY_CODE: "无效的核销码",
    ErrorCode.VERIFY_CODE_EXPIRED: "核销码已过期",
    ErrorCode.PAY_FAILED: "支付失败",
    ErrorCode.REFUND_FAILED: "退款失败",
    ErrorCode.CHANNEL_ERROR: "支付渠道异常",
    ErrorCode.SLOT_FULL: "该时段已约满",
    ErrorCode.RESERVATION_NOT_FOUND: "预约不存在",
    ErrorCode.RESERVATION_STATUS_INVALID: "预约状态非法",
    ErrorCode.SYSTEM_ERROR: "系统错误",
}

# 错误码 -> 默认 HTTP 状态码（认证类用真实状态码，业务类统一 200 便于客户端解析 code）
_HTTP_STATUS: dict[int, int] = {
    ErrorCode.INVALID_TOKEN: 401,
    ErrorCode.TOKEN_EXPIRED: 401,
    ErrorCode.NO_PERMISSION: 403,
}


class BizError(Exception):
    """业务异常。携带业务 code、文案与可选 HTTP 状态码。"""

    def __init__(
        self,
        code: int | ErrorCode,
        message: str | None = None,
        http_status: int | None = None,
        data: object | None = None,
    ) -> None:
        self.code = int(code)
        self.message = message or _DEFAULT_MESSAGES.get(self.code, "业务错误")
        self.http_status = http_status or _HTTP_STATUS.get(self.code, 200)
        self.data = data
        super().__init__(self.message)
