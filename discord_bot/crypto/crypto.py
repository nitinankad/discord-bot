from __future__ import annotations

import hashlib

# ── Ed25519 constants ──
P = 2**255 - 19
Q = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, P - 2, P) % P

# Base point in extended coordinates (X:Y:Z:T)
_Gy = 4 * pow(5, P - 2, P) % P
_Gx_sq = (_Gy * _Gy - 1) * pow(D * _Gy * _Gy + 1, P - 2, P) % P
_Gx = pow(_Gx_sq, (P + 3) // 8, P)
if (_Gx * _Gx - _Gx_sq) % P != 0:
    _Gx = _Gx * pow(2, (P - 1) // 4, P) % P
if _Gx & 1:
    _Gx = P - _Gx
G = (_Gx, _Gy, 1, _Gx * _Gy % P)


def _point_add(P1, P2):
    x1, y1, z1, t1 = P1
    x2, y2, z2, t2 = P2
    a = (y1 - x1) * (y2 - x2) % P
    b = (y1 + x1) * (y2 + x2) % P
    c = 2 * D * t1 * t2 % P
    d = 2 * z1 * z2 % P
    e, f, g, h = b - a, d - c, d + c, b + a
    return e * f % P, g * h % P, f * g % P, e * h % P


def _point_mul(s, pt):
    result = (0, 1, 1, 0)  # identity
    while s:
        if s & 1:
            result = _point_add(result, pt)
        pt = _point_add(pt, pt)
        s >>= 1
    return result


def _point_equal(P1, P2):
    return (
        (P1[0] * P2[2] - P2[0] * P1[2]) % P == 0 and
        (P1[1] * P2[2] - P2[1] * P1[2]) % P == 0
    )


def _decode_point(b):
    if len(b) != 32:
        return None
    val = int.from_bytes(b, 'little')
    sign = val >> 255
    y = val & ((1 << 255) - 1)

    y2 = y * y % P
    x2 = (y2 - 1) * pow(D * y2 + 1, P - 2, P) % P
    if x2 == 0:
        return (0, y, 1, 0) if not sign else None

    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0:
        x = x * pow(2, (P - 1) // 4, P) % P
    if (x * x - x2) % P != 0:
        return None
    if x & 1 != sign:
        x = P - x
    return (x, y, 1, x * y % P)


def ed25519_verify(public_key_hex, message_bytes, signature_hex):
    try:
        pub = bytes.fromhex(public_key_hex)
        sig = bytes.fromhex(signature_hex)
    except ValueError:
        return False

    if len(pub) != 32 or len(sig) != 64:
        return False

    A = _decode_point(pub)
    R = _decode_point(sig[:32])
    if A is None or R is None:
        return False

    s = int.from_bytes(sig[32:], 'little')
    if s >= Q:
        return False

    k = int.from_bytes(
        hashlib.sha512(sig[:32] + pub + message_bytes).digest(), 'little'
    ) % Q

    return _point_equal(_point_mul(s, G), _point_add(R, _point_mul(k, A)))
