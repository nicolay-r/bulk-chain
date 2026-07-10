import sys
import unittest
from os.path import dirname, join, realpath

sys.path.insert(0, join(dirname(realpath(__file__)), ".."))
sys.path.insert(0, join(dirname(realpath(__file__)), "../.."))

from providers.replicate_vlm import ReplicateVLM
from utils import default_vlm_llm


TEST_DIR = join(dirname(realpath(__file__)), "..")
IMAGE_PATH = join(TEST_DIR, "data", "example.jpg")
PROMPT = "describe image"


class TestReplicateVLM(unittest.TestCase):

    def setUp(self):
        self.provider = ReplicateVLM.__new__(ReplicateVLM)
        self.provider.settings = {
            "system_prompt": "",
            "reasoning_effort": "medium",
            "max_completion_tokens": 4096,
        }
        self.provider.image_param = "image_input"

    def test_build_input_with_images_url(self):
        payload = self.provider._build_input(
            "Describe the image",
            images=IMAGE_PATH,
        )

        self.assertEqual(payload["prompt"], "Describe the image")
        self.assertEqual(payload["image_input"], [IMAGE_PATH])

    def test_build_input_with_image_alias(self):
        payload = self.provider._build_input(
            "Describe the image",
            image=IMAGE_PATH,
        )

        self.assertEqual(payload["image_input"], [IMAGE_PATH])

    def test_build_input_without_images(self):
        payload = self.provider._build_input("Hello")

        self.assertEqual(payload["prompt"], "Hello")
        self.assertNotIn("image_input", payload)


class TestReplicateVLMIntegration(unittest.TestCase):

    llm = default_vlm_llm()

    def test_describe_image(self):
        with open(IMAGE_PATH, "rb") as image:
            response = self.llm.ask(PROMPT, images=image)

        self.assertIsInstance(response, str)
        self.assertGreater(len(response.strip()), 0)
        print(response)

    def test_describe_image_stream(self):
        with open(IMAGE_PATH, "rb") as image:
            chunks = self.llm.ask_stream(PROMPT, images=image)
            response = "".join(str(chunk) for chunk in chunks)

        self.assertIsInstance(response, str)
        self.assertGreater(len(response.strip()), 0)
        print(response)


if __name__ == '__main__':
    unittest.main()
