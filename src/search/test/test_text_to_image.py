import unittest
from ml.pipeline.imageToText import ImageToTextPipeline


class TestTextToImagePipeline(unittest.TestCase):
    def test_normal_image(self):
        texts, labels = ImageToTextPipeline().generate(
            "https://freerangestock.com/sample/22169/happy-woman-with-purse.jpg"
        )
        print(texts)
        print(labels)
        self.assertGreater(len(texts), 0)
        self.assertGreater(len(labels), 0)


if __name__ == "__main__":
    unittest.main()
