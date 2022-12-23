import unittest
from common.helper import CommonHelper
from common.source_location import SourceLocation


class TestSourceLocation(unittest.TestCase):
    def test_source_location(self):
        self.assertEqual(
            CommonHelper().get_source_location(text="https://google.com"),
            SourceLocation.URL,
        )
        self.assertEqual(
            CommonHelper().get_source_location(text="http://google.com"),
            SourceLocation.URL,
        )
        self.assertEqual(
            CommonHelper().get_source_location(text="../search/"),
            SourceLocation.FILE_SYSTEM,
        )
        self.assertEqual(
            CommonHelper().get_source_location(text="./test/"),
            SourceLocation.FILE_SYSTEM,
        )
        self.assertEqual(
            CommonHelper().get_source_location(
                text="s3://bucket_name/folder1/folder2/file1.json"
            ),
            SourceLocation.S3,
        )

    def test_s3_is_valid(self):
        self.assertEqual(
            CommonHelper()._is_s3_path_valid(
                text="s3://bucket_name/folder1/folder2/file1.json"
            ),
            False,
        )
        self.assertEqual(
            CommonHelper()._is_s3_path_valid(
                text="s3://s3-website-bucket-d579ef7/index.html"
            ),
            True,
        )


if __name__ == "__main__":
    unittest.main()
