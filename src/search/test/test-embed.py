import unittest
from ml.pipeline.embed import EmbedPipeline
from environment import Environment


class TestEmbedPipeline(unittest.TestCase):
    def test_normal_text(self):
        (
            text_embedding,
            context_embedding,
            label_embedding,
            text_generated,
            label_generated,
        ) = EmbedPipeline().encode("hello")
        self.assertEqual(len(text_embedding.tolist()), 512)

    def test_normal_image(self):
        (
            text_embedding,
            context_embedding,
            label_embedding,
            text_generated,
            label_generated,
        ) = EmbedPipeline().encode(
            "https://cdn-v4.petpetgo.com/600/public/333311c4-c5eb-48a7-a742-6750d9eb00a3.jpg"
        )
        self.assertEqual(len(text_embedding.tolist()), 512)
        self.assertEqual(len(label_embedding.tolist()), 512)
        self.assertEqual(len(context_embedding.tolist()), 1000)

    def test_broken_image(self):
        (
            text_embedding,
            context_embedding,
            label_embedding,
            text_generated,
            label_generated,
        ) = EmbedPipeline().encode(
            "http://img5a.flixcart.com/image/fabric/h/k/a/r-c-lehe-bt-indcrown-1000x1000-imaejbczsqzjrbfd.jpeg"
        )
        self.assertEqual(len(text_embedding.tolist()), 512)
        self.assertEqual(len(label_embedding.tolist()), 512)
        self.assertEqual(len(context_embedding.tolist()), 1000)


if __name__ == "__main__":
    unittest.main()
