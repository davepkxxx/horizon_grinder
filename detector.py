import logging

from rapidocr_onnxruntime import RapidOCR
import numpy as np

logger = logging.getLogger("grinder")

_ocr = None


def _get_ocr() -> RapidOCR:
    global _ocr
    if _ocr is None:
        _ocr = RapidOCR()
    return _ocr


def detect_trigger(
    image: np.ndarray,
    trigger_texts: list[str],
    confidence_threshold: float = 0.7,
) -> bool:
    ocr = _get_ocr()
    result, _ = ocr(image)
    if not result:
        return False

    for box, text, conf in result:
        if conf < confidence_threshold:
            continue
        for trigger in trigger_texts:
            if trigger in text:
                logger.debug(f"OCR match: '{text}' (conf={conf:.2f}) contains '{trigger}'")
                return True
    return False
