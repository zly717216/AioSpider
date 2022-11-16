from AioSpider.utils_pkg.cchardet import _cchardet


def detect(msg: bytes) -> dict:
    """
    推测编码
    :params msg: 推测内容
    :returns: {"encoding": str, "confidence": float}
    """

    encoding, confidence = _cchardet.detect_with_confidence(msg)
    if isinstance(encoding, bytes):
        encoding = encoding.decode()
    return {"encoding": encoding, "confidence": confidence}


class UniversalDetector(object):
    def __init__(self):
        self._detector = _cchardet.UniversalDetector()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        return False

    def reset(self):
        self._detector.reset()

    def feed(self, data):
        self._detector.feed(data)

    def close(self):
        self._detector.close()

    @property
    def done(self):
        return self._detector.done

    @property
    def result(self):
        encoding, confidence = self._detector.result
        if isinstance(encoding, bytes):
            encoding = encoding.decode()
        return {"encoding": encoding, "confidence": confidence}
