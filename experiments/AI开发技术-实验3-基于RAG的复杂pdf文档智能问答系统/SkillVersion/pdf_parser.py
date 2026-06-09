"""
pdf_parser.py — PDF解析器
参考: 自定义 pdf-parser skill (MySkills)
核心原则: PyMuPDF 主引擎, EasyOCR 图片识别, 页眉页脚清洗
"""
import io
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np

from config import Config

logger = logging.getLogger(__name__)


class PDFParser:
    """使用 PyMuPDF 解析 PDF，EasyOCR 识别图表文字"""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
        self._fitz_doc = None
        self._ocr_reader = None

    @property
    def fitz_doc(self):
        if self._fitz_doc is None:
            import fitz
            self._fitz_doc = fitz.open(str(self.pdf_path))
        return self._fitz_doc

    @property
    def ocr_reader(self):
        if self._ocr_reader is None:
            try:
                import easyocr
                logger.info("正在初始化 EasyOCR（首次加载需下载模型）...")
                self._ocr_reader = easyocr.Reader(
                    ["ch_sim", "en"], gpu=False, verbose=False
                )
                logger.info("EasyOCR 初始化完成")
            except ImportError:
                logger.warning("EasyOCR 未安装，图片 OCR 将被跳过")
                self._ocr_reader = False
            except Exception as e:
                logger.warning(f"EasyOCR 初始化失败: {e}")
                self._ocr_reader = False
        return self._ocr_reader if self._ocr_reader is not False else None

    @property
    def total_pages(self) -> int:
        return self.fitz_doc.page_count

    def close(self):
        if self._fitz_doc:
            self._fitz_doc.close()

    # ---------- 文本提取 ----------

    def extract_text(self, page_num: int) -> str:
        """使用 PyMuPDF 提取页面文本并清洗页眉页脚"""
        page = self.fitz_doc[page_num]
        text = page.get_text("text")
        if not text:
            return ""

        lines = text.strip().split("\n")
        cleaned = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if s == "敬请阅读最后一页特别声明":
                continue
            if s.startswith("证券研究报告") or s.startswith("金融工程"):
                continue
            if s.startswith("-") and s.endswith("-") and len(s) <= 5:
                continue
            cleaned.append(line)

        return "\n".join(cleaned).strip()

    # ---------- 图片提取 ----------

    def extract_images(self, page_num: int) -> List[Dict]:
        """提取页面中的图片，过滤小图标"""
        page = self.fitz_doc[page_num]
        images = []

        for img_idx, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            try:
                base_image = self.fitz_doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]
                w, h = base_image.get("width", 0), base_image.get("height", 0)

                if w < 100 and h < 100:
                    continue

                img_hash = hashlib.md5(image_bytes).hexdigest()[:12]
                filename = f"p{page_num + 1}_img{img_idx}_{img_hash}.{ext}"
                img_path = Config.IMAGES_DIR / filename
                with open(img_path, "wb") as f:
                    f.write(image_bytes)

                images.append({
                    "page": page_num + 1,
                    "index": img_idx,
                    "path": str(img_path),
                    "filename": filename,
                    "width": w,
                    "height": h,
                    "bytes": image_bytes,
                })
            except Exception as e:
                logger.warning(f"提取图片失败 (page={page_num + 1}, img={img_idx}): {e}")

        return images

    def ocr_image(self, image_bytes: bytes) -> str:
        """对图片运行 EasyOCR 提取文字"""
        reader = self.ocr_reader
        if reader is None:
            return ""

        try:
            from PIL import Image
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            results = reader.readtext(image_np)
            texts = [r[1] for r in results if r[2] >= 0.3]
            return " ".join(texts)
        except Exception as e:
            logger.warning(f"OCR 失败: {e}")
            return ""

    # ---------- 联合解析 ----------

    def parse(self) -> Tuple[List[Dict], List[Dict]]:
        text_docs = []
        image_docs = []

        for page_num in range(self.total_pages):
            page_no = page_num + 1
            logger.info(f"解析第 {page_no}/{self.total_pages} 页...")

            page_text = self.extract_text(page_num)
            if page_text:
                text_docs.append({
                    "text": page_text,
                    "metadata": {
                        "page": page_no,
                        "type": "text",
                        "source": self.pdf_path.name,
                    },
                })

            for img in self.extract_images(page_num):
                ocr_text = self.ocr_image(img["bytes"])
                desc_parts = [
                    f"[图片] 位于第 {img['page']} 页",
                    f"尺寸: {img['width']}x{img['height']}",
                ]
                if ocr_text:
                    desc_parts.append(f"OCR 识别文字: {ocr_text}")
                else:
                    desc_parts.append("(该图片无可识别文字，可能为纯图表)")

                image_docs.append({
                    "text": "；".join(desc_parts),
                    "metadata": {
                        "page": img["page"],
                        "type": "image",
                        "image_path": img["path"],
                        "filename": img["filename"],
                        "ocr_text": ocr_text,
                        "width": img["width"],
                        "height": img["height"],
                        "source": self.pdf_path.name,
                    },
                })

        logger.info(f"解析完成: 文本 {len(text_docs)} 页, 图片 {len(image_docs)} 张")
        return text_docs, image_docs
