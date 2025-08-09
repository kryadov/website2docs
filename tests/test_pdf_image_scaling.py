import os
import io
import base64
import unittest
from PIL import Image

from website2docs import save_as_pdf, PageContent


def _make_data_uri_png(width=5000, height=5000, color=(0, 128, 255)):
    img = Image.new('RGB', (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return f"data:image/png;base64,{b64}"


def _make_page_with_large_image(paragraphs_before=60, paragraphs_after=10):
    # Add a lot of paragraphs before so the image is likely placed mid-page
    paras = ''.join(f"<p>Paragraph {i} Lorem ipsum dolor sit amet.</p>" for i in range(paragraphs_before))
    data_uri = _make_data_uri_png(6000, 4000)
    img_html = f"<img src=\"{data_uri}\" alt=\"big\">"
    tail = ''.join(f"<p>Tail {i}</p>" for i in range(paragraphs_after))
    html = f"<main>{paras}{img_html}{tail}</main>"

    page = PageContent(url="https://example.com", title="Test Page", text="")
    # attach HTML so rich extraction is used
    setattr(page, 'html', html)
    return page


class TestPDFImageScaling(unittest.TestCase):
    def setUp(self):
        self.out_dir = os.path.join(os.getcwd(), 'test_outputs')
        os.makedirs(self.out_dir, exist_ok=True)

    def _run_and_assert_pdf(self, orientation: str):
        pages = [_make_page_with_large_image()]
        out_path = os.path.join(self.out_dir, f'pdf_with_large_image_{orientation}.pdf')
        # Remove if exists
        try:
            if os.path.exists(out_path):
                os.remove(out_path)
        except Exception:
            pass
        # This should not raise
        save_as_pdf(pages, out_path, start_url=pages[0].url, orientation=orientation)
        # File created and non-trivial size
        self.assertTrue(os.path.exists(out_path), 'PDF file was not created')
        self.assertGreater(os.path.getsize(out_path), 1024, 'PDF file too small; likely not written correctly')

    def test_pdf_image_scaling_portrait(self):
        self._run_and_assert_pdf('portrait')

    def test_pdf_image_scaling_landscape(self):
        self._run_and_assert_pdf('landscape')


if __name__ == '__main__':
    unittest.main()
