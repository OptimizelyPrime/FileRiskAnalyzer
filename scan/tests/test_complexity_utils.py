import unittest
from unittest.mock import patch, MagicMock, mock_open
from common.utils.complexity_utils import analyze_file_complexity, parse_complexity_report

class TestComplexityUtils(unittest.TestCase):

    @patch('common.utils.complexity_utils.open', new_callable=mock_open, read_data='def f(): pass')
    @patch('maintainability_score_analyzer.analyze')
    def test_analyze_file_complexity(self, mock_analyze, mock_file_open):
        mock_analyze.return_value = {
            'functions': [
                {
                    'name': 'f',
                    'cyclomatic_complexity': 1,
                    'length': 1,
                    'parameters': 0,
                    'maintainability_index': 100
                }
            ]
        }

        result = analyze_file_complexity('dummy_path.py')

        self.assertIn('f', result)
        self.assertEqual(result['f']['cyclomatic_complexity'], 1)
        self.assertEqual(result['f']['maintainability_index'], 100)

    def test_parse_complexity_report(self):
        report_content = """
# Repository Complexity and Maintainability Report

## file1.py

| Churn | Knowledge Score | Developer | File Health Score |
|-------|-----------------|-----------|-------------------|
| 10 | 80% | user@example.com | 90.5 |

**func1**: Maintainability Index = 85.0
| Lines Of Code | Halstead Volume | Cyclomatic Complexity |
|---|---|---|
| 10 | 100.0 | 5 |

**func2**: Maintainability Index = 95.0
| Lines Of Code | Halstead Volume | Cyclomatic Complexity |
|---|---|---|
| 5 | 50.0 | 2 |

## file2.py

| Churn | Knowledge Score | Developer | File Health Score |
|-------|-----------------|-----------|-------------------|
| 5 | 90% | another_user@example.com | 95.0 |

**func3**: Maintainability Index = 90.0
| Lines Of Code | Halstead Volume | Cyclomatic Complexity |
|---|---|---|
| 8 | 80.0 | 3 |
"""

        result = parse_complexity_report(report_content)

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['file'], 'file1.py')
        self.assertEqual(result[0]['churn'], 10)
        self.assertEqual(result[0]['knowledge_score'], '80')
        self.assertEqual(result[0]['developer'], 'user@example.com')
        self.assertEqual(result[0]['file_health'], 90.5)
        self.assertEqual(len(result[0]['functions']), 2)
        self.assertEqual(result[0]['functions'][0]['function'], 'func1')
        self.assertEqual(result[0]['functions'][0]['maintainability_index'], 85.0)
        self.assertEqual(result[0]['functions'][0]['cyclomatic_complexity'], 5)

        self.assertEqual(result[1]['file'], 'file2.py')
        self.assertEqual(result[1]['churn'], 5)

if __name__ == '__main__':
    unittest.main()
