import unittest
from os.path import join

from tqdm import tqdm

from bulk_chain.api import CWD, iter_content
from bulk_chain.core.utils import dynamic_init
from bulk_chain.core.utils_logger import StreamedLogger
from utils import API_TOKEN, iter_test_jsonl_samples


class TestAPI_Streaming(unittest.TestCase):

    llm = dynamic_init(class_dir=join(CWD, ".."),
                       class_filepath="providers/replicate_104.py",
                       class_name="Replicate")(api_token=API_TOKEN,
                                               model_name="meta/meta-llama-3-70b-instruct",
                                               stream=True)

    def test_iter(self):

        streamed_logger = StreamedLogger(__name__)

        def callback(chunk, info, reg):

            if info["param"] not in reg:
                current_field = info["param"]
                streamed_logger.info(f"\n{current_field} (batch_ind={info['ind']}):\n")
                reg.add(info["param"])

            streamed_logger.info(chunk)

        reg = set()
        input_dicts_it = iter_test_jsonl_samples()
        data_it = iter_content(input_dicts_it=input_dicts_it,
                               llm=self.llm,
                               return_batch=False,
                               callback_stream_func=lambda chunk, info: callback(chunk, info, reg),
                               schema="schema/thor_cot_schema.json")

        for _ in tqdm(data_it):
            reg.clear()
            streamed_logger.info("\n|NEXT ENTRY|\n")
