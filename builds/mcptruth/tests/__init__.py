"""Tests for the MCPTruth build."""

import os
import sys

# Allow `python -m tests.mock_mcp_server` and test imports from the build root.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)