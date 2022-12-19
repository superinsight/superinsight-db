import unittest
from ml.pipeline.imageToText import ImageToTextPipeline


class TestTextToImagePipeline(unittest.TestCase):
    def test_normal_image(self):
        texts, labels = ImageToTextPipeline().generate(
            "https://freerangestock.com/sample/22169/happy-woman-with-purse.jpg"
        )
        self.assertGreater(len(texts), 0)
        self.assertGreater(len(labels), 0)

    def test_broken_image(self):
        texts, labels = ImageToTextPipeline().generate(
            "http://img5a.flixcart.com/image/fabric/h/k/a/r-c-lehe-bt-indcrown-1000x1000-imaejbczsqzjrbfd.jpeg"
        )
        self.assertEqual(len(texts), 0)
        self.assertEqual(len(labels), 0)


if __name__ == "__main__":
    unittest.main()
