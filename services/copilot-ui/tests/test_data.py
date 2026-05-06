from unittest.mock import patch

import pandas as pd
from src.data import load_token_usages


class TestData:
    @patch("src.data.engine.connect")
    @patch("src.data.pd.read_sql")
    def test_load_token_usages(self, mock_read_sql, *_mock_args):
        mock_read_sql.return_value = pd.DataFrame({"total_tokens": [10, 20]})

        df = load_token_usages()
        assert len(df) == 2
        assert mock_read_sql.called
