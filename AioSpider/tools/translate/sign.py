class TranslateSign:

    @staticmethod
    def shift_operation(t: int, e: str) -> int:
        for idx in range(0, len(e) - 2, 3):
            r = ord(e[idx + 2]) - 87 if 'a' <= e[idx + 2] else int(e[idx + 2])
            r = t >> r if '+' == e[idx + 1] else t << r
            t = (t + r) & 0xFFFFFFFF if '+' == e[idx] else t ^ r
        return t

    @staticmethod
    def truncate_text(t: str) -> str:
        length = len(t)
        if length > 30:
            t = t[:10] + t[length // 2 - 5: length // 2 + 5] + t[-10:]
        return t

    @staticmethod
    def get_encoded_list(t: str) -> list:
        encoded_list = []
        for y in range(len(t)):
            w = ord(t[y])
            if w < 128:
                encoded_list.append(w)
            else:
                if w < 2048:
                    encoded_list.append((w >> 6) | 192)
                elif 0xD800 <= w <= 0xDBFF and y + 1 < len(t) and 0xDC00 <= ord(t[y + 1]) <= 0xDFFF:
                    w = 0x10000 + ((w & 0x3FF) << 10) + (ord(t[y + 1]) & 0x3FF)
                    encoded_list.extend([(w >> 18) | 240, ((w >> 12) & 0x3F) | 128])
                    y += 1
                else:
                    encoded_list.append((w >> 12) | 224)
                encoded_list.extend([((w >> 6) & 0x3F) | 128, (w & 0x3F) | 128])
        return encoded_list
    
    @classmethod
    def get_sign(cls, query: str) -> str:
        
        t = cls.truncate_text(query)
        h, m = 320305, 131321201
        encoded_list = cls.get_encoded_list(t)
    
        b = h
        x = "+-a^+6"
        k = "+-3^+b+-f"
    
        for _ in encoded_list:
            b = cls.shift_operation(b + _, x)
    
        b = cls.shift_operation(b, k) ^ m
        if b < 0:
            b = 0x80000000 + (b & 0x7FFFFFFF)
        b %= 1000000
    
        return f"{b}.{b ^ h}"


def get_sign(query: str) -> str:
    return TranslateSign.get_sign(query)
