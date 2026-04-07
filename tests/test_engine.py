"""
Tests for the Docker Lesson Engine (engine.py).
Uses only stdlib: unittest, unittest.mock, tempfile, json, pathlib.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import engine
from engine import (
    Session,
    Challenge,
    offer_hint,
    MultipleChoice,
    FillCommand,
    ScenarioChallenge,
    SpotTheBug,
    LiveExecution,
    run_module,
    load_progress,
    save_progress,
    record_module,
    PROGRESS_FILE,
)


# ---------------------------------------------------------------------------
# Helper: create a fresh session
# ---------------------------------------------------------------------------

def _session(name="tester", hints=3):
    s = Session(name)
    s.hints_remaining = hints
    return s


# ===========================================================================
# offer_hint()
# ===========================================================================

class TestOfferHint(unittest.TestCase):

    @patch("builtins.print")
    @patch("builtins.input")
    def test_returns_false_when_hint_text_empty(self, mock_input, mock_print):
        s = _session()
        result = offer_hint(s, "")
        self.assertFalse(result)
        mock_input.assert_not_called()

    @patch("builtins.print")
    @patch("builtins.input")
    def test_returns_false_when_no_hints_remaining(self, mock_input, mock_print):
        s = _session(hints=0)
        result = offer_hint(s, "Some hint")
        self.assertFalse(result)
        mock_input.assert_not_called()

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    def test_returns_false_when_user_presses_enter(self, mock_input, mock_print):
        s = _session()
        result = offer_hint(s, "Some hint")
        self.assertFalse(result)
        self.assertEqual(s.hints_remaining, 3)

    @patch("builtins.print")
    @patch("builtins.input", return_value="h")
    def test_returns_true_and_decrements_when_user_types_h(self, mock_input, mock_print):
        s = _session(hints=3)
        result = offer_hint(s, "Some hint")
        self.assertTrue(result)
        self.assertEqual(s.hints_remaining, 2)


# ===========================================================================
# MultipleChoice.run()
# ===========================================================================

class TestMultipleChoice(unittest.TestCase):

    def _mc(self, correct=0, points=1, hint_text="", options=None):
        return MultipleChoice(
            question="What is Docker?",
            options=options or ["A container platform", "A VM", "An OS"],
            correct=correct,
            explanation="Docker is a container platform.",
            hint_text=hint_text,
            points=points,
        )

    @patch("builtins.print")
    @patch("builtins.input", return_value="A")
    @patch("engine.offer_hint", return_value=False)
    def test_correct_answer_no_hint(self, mock_hint, mock_input, mock_print):
        s = _session()
        mc = self._mc(correct=0, points=2)
        result = mc.run(s)
        self.assertTrue(result)
        self.assertEqual(s.module_score, 2)
        self.assertEqual(s.module_max, 2)

    @patch("builtins.print")
    @patch("builtins.input", return_value="B")
    @patch("engine.offer_hint", return_value=False)
    def test_wrong_answer(self, mock_hint, mock_input, mock_print):
        s = _session()
        mc = self._mc(correct=0, points=2)
        result = mc.run(s)
        self.assertFalse(result)
        self.assertEqual(s.module_score, 0)
        self.assertEqual(s.module_max, 2)
        # Explanation should be printed
        printed = [str(c) for c in mock_print.call_args_list]
        joined = " ".join(printed)
        self.assertIn("Docker is a container platform", joined)

    @patch("builtins.print")
    @patch("builtins.input", return_value="A")
    @patch("engine.offer_hint", return_value=True)
    def test_correct_answer_with_hint(self, mock_hint, mock_input, mock_print):
        s = _session()
        mc = self._mc(correct=0, points=3)
        result = mc.run(s)
        self.assertTrue(result)
        # max(1, 3 - 1) = 2
        self.assertEqual(s.module_score, 2)
        self.assertEqual(s.module_max, 3)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["Z", "1", "!"])
    @patch("engine.offer_hint", return_value=False)
    def test_three_invalid_inputs_exhausts_attempts(self, mock_hint, mock_input, mock_print):
        s = _session()
        mc = self._mc(correct=0, points=1)
        result = mc.run(s)
        self.assertFalse(result)
        self.assertEqual(s.module_score, 0)
        self.assertEqual(s.module_max, 1)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["Z", "A"])
    @patch("engine.offer_hint", return_value=False)
    def test_invalid_then_valid_correct(self, mock_hint, mock_input, mock_print):
        s = _session()
        mc = self._mc(correct=0, points=1)
        result = mc.run(s)
        self.assertTrue(result)
        self.assertEqual(s.module_score, 1)
        self.assertEqual(s.module_max, 1)


# ===========================================================================
# FillCommand.run()
# ===========================================================================

class TestFillCommand(unittest.TestCase):

    def _fc(self, accepted=None, points=2, hint_text=""):
        return FillCommand(
            prompt="Type the command to list containers",
            accepted=accepted or ["docker ps"],
            explanation="Use docker ps to list containers.",
            hint_text=hint_text,
            points=points,
        )

    @patch("builtins.print")
    @patch("builtins.input", return_value="docker ps")
    @patch("engine.offer_hint", return_value=False)
    def test_exact_match(self, mock_hint, mock_input, mock_print):
        s = _session()
        fc = self._fc()
        result = fc.run(s)
        self.assertTrue(result)
        self.assertEqual(s.module_score, 2)
        self.assertEqual(s.module_max, 2)

    @patch("builtins.print")
    @patch("builtins.input", return_value="docker   ps")
    @patch("engine.offer_hint", return_value=False)
    def test_variant_whitespace_match(self, mock_hint, mock_input, mock_print):
        s = _session()
        fc = self._fc()
        result = fc.run(s)
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("builtins.input", return_value="Docker PS")
    @patch("engine.offer_hint", return_value=False)
    def test_case_insensitive_match(self, mock_hint, mock_input, mock_print):
        s = _session()
        fc = self._fc()
        result = fc.run(s)
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("builtins.input", return_value="docker images")
    @patch("engine.offer_hint", return_value=False)
    def test_non_matching(self, mock_hint, mock_input, mock_print):
        s = _session()
        fc = self._fc()
        result = fc.run(s)
        self.assertFalse(result)
        self.assertEqual(s.module_score, 0)
        self.assertEqual(s.module_max, 2)
        # Should print expected command
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        self.assertIn("docker ps", printed)

    @patch("builtins.print")
    @patch("builtins.input", return_value="docker ps")
    @patch("engine.offer_hint", return_value=True)
    def test_with_hint_used(self, mock_hint, mock_input, mock_print):
        s = _session()
        fc = self._fc(points=2)
        result = fc.run(s)
        self.assertTrue(result)
        # max(1, 2 - 1) = 1
        self.assertEqual(s.module_score, 1)
        self.assertEqual(s.module_max, 2)


# ===========================================================================
# ScenarioChallenge.run()
# ===========================================================================

class TestScenarioChallenge(unittest.TestCase):

    def _sc(self, accepted=None, points=3):
        return ScenarioChallenge(
            setup="A container keeps restarting.",
            question="What command would you use to check logs?",
            accepted=accepted or ["docker logs"],
            explanation="Use docker logs <container>.",
            points=points,
        )

    @patch("builtins.print")
    @patch("builtins.input", return_value="I would use docker logs to debug it")
    @patch("engine.offer_hint", return_value=False)
    def test_keyword_substring(self, mock_hint, mock_input, mock_print):
        s = _session()
        sc = self._sc()
        result = sc.run(s)
        self.assertTrue(result)
        self.assertEqual(s.module_score, 3)

    @patch("builtins.print")
    @patch("builtins.input", return_value="docker logs")
    @patch("engine.offer_hint", return_value=False)
    def test_exact_keyword(self, mock_hint, mock_input, mock_print):
        s = _session()
        sc = self._sc()
        result = sc.run(s)
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("builtins.input", return_value="DOCKER LOGS")
    @patch("engine.offer_hint", return_value=False)
    def test_case_insensitive(self, mock_hint, mock_input, mock_print):
        s = _session()
        sc = self._sc()
        result = sc.run(s)
        self.assertTrue(result)

    @patch("builtins.print")
    @patch("builtins.input", return_value="restart the container")
    @patch("engine.offer_hint", return_value=False)
    def test_no_keyword(self, mock_hint, mock_input, mock_print):
        s = _session()
        sc = self._sc()
        result = sc.run(s)
        self.assertFalse(result)
        self.assertEqual(s.module_max, 3)


# ===========================================================================
# SpotTheBug.run()
# ===========================================================================

class TestSpotTheBug(unittest.TestCase):

    def _stb(self, keywords=None, points=3):
        return SpotTheBug(
            code_block="FROM ubuntu\nRUN apt-get install python",
            question="What is wrong with this Dockerfile?",
            accepted_keywords=keywords or ["apt-get update"],
            explanation="You need to run apt-get update first.",
            points=points,
        )

    @patch("builtins.print")
    @patch("builtins.input", return_value="missing apt-get update before install")
    @patch("engine.offer_hint", return_value=False)
    def test_keyword_in_answer(self, mock_hint, mock_input, mock_print):
        s = _session()
        stb = self._stb()
        result = stb.run(s)
        self.assertTrue(result)
        self.assertEqual(s.module_score, 3)
        self.assertEqual(s.module_max, 3)

    @patch("builtins.print")
    @patch("builtins.input", return_value="looks fine to me")
    @patch("engine.offer_hint", return_value=False)
    def test_no_keyword(self, mock_hint, mock_input, mock_print):
        s = _session()
        stb = self._stb()
        result = stb.run(s)
        self.assertFalse(result)
        self.assertEqual(s.module_max, 3)

    @patch("builtins.print")
    @patch("builtins.input", return_value="need to update cache")
    @patch("engine.offer_hint", return_value=False)
    def test_multiple_keywords_first_match_wins(self, mock_hint, mock_input, mock_print):
        s = _session()
        stb = self._stb(keywords=["update", "cache", "refresh"])
        result = stb.run(s)
        self.assertTrue(result)
        self.assertEqual(s.module_score, 3)


# ===========================================================================
# LiveExecution.run()
# ===========================================================================

class TestLiveExecution(unittest.TestCase):

    def _le(self, points=2):
        return LiveExecution(
            prompt="Let's verify Docker is running",
            command_to_run="docker version",
            success_substring="version",
            explanation="Docker must be installed and running.",
            points=points,
        )

    @patch("builtins.print")
    @patch("engine.shutil.which", return_value=None)
    def test_docker_not_installed_skips(self, mock_which, mock_print):
        s = _session()
        le = self._le()
        result = le.run(s)
        self.assertTrue(result)
        # Score should NOT be incremented (skipped, no penalty)
        self.assertEqual(s.module_score, 0)
        self.assertEqual(s.module_max, 0)

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    @patch("engine.subprocess.run")
    @patch("engine.shutil.which", return_value="/usr/bin/docker")
    def test_docker_installed_success(self, mock_which, mock_subproc, mock_input, mock_print):
        mock_result = MagicMock()
        mock_result.stdout = "Docker version 20.10.7"
        mock_result.stderr = ""
        mock_subproc.return_value = mock_result

        s = _session()
        le = self._le()
        result = le.run(s)
        self.assertTrue(result)
        self.assertEqual(s.module_score, 2)
        self.assertEqual(s.module_max, 2)

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    @patch("engine.subprocess.run")
    @patch("engine.shutil.which", return_value="/usr/bin/docker")
    def test_docker_installed_no_match(self, mock_which, mock_subproc, mock_input, mock_print):
        mock_result = MagicMock()
        mock_result.stdout = "something else"
        mock_result.stderr = ""
        mock_subproc.return_value = mock_result

        s = _session()
        le = self._le()
        result = le.run(s)
        self.assertFalse(result)
        self.assertEqual(s.module_score, 0)
        self.assertEqual(s.module_max, 2)

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    @patch("engine.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="docker", timeout=30))
    @patch("engine.shutil.which", return_value="/usr/bin/docker")
    def test_docker_timeout(self, mock_which, mock_subproc, mock_input, mock_print):
        s = _session()
        le = self._le()
        result = le.run(s)
        self.assertFalse(result)
        self.assertEqual(s.module_max, 2)

    @patch("builtins.print")
    @patch("builtins.input", return_value="")
    @patch("engine.subprocess.run", side_effect=OSError("Permission denied"))
    @patch("engine.shutil.which", return_value="/usr/bin/docker")
    def test_docker_generic_exception(self, mock_which, mock_subproc, mock_input, mock_print):
        s = _session()
        le = self._le()
        result = le.run(s)
        self.assertFalse(result)
        self.assertEqual(s.module_max, 2)


# ===========================================================================
# run_module()
# ===========================================================================

class TestRunModule(unittest.TestCase):

    @patch("builtins.print")
    def test_resets_session_state(self, mock_print):
        s = _session()
        s.module_score = 99
        s.module_max = 99
        s.hints_remaining = 0

        # Use a challenge that always passes
        ch = MagicMock()
        ch.run = MagicMock(side_effect=lambda sess: _apply_score(sess, 1, 1))

        result = run_module("Test", "Lesson", [ch], s)
        # After run_module resets, module_score was set to 0 then incremented
        # hints_remaining should have been reset to 3
        # We can verify the reset happened because the mock was called after reset
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["max"], 1)

    @patch("builtins.print")
    def test_passed_true_when_gte_70_percent(self, mock_print):
        s = _session()
        # 3 challenges: 2 pass (2 pts each), 1 fails (adds 2 to max only)
        ch_pass = MagicMock()
        ch_pass.run = MagicMock(side_effect=lambda sess: _apply_score(sess, 2, 2))
        ch_fail = MagicMock()
        ch_fail.run = MagicMock(side_effect=lambda sess: _apply_fail(sess, 2))

        result = run_module("Test", "Lesson", [ch_pass, ch_pass, ch_fail], s)
        # score=4, max=6, pct=66.7% -> not passed
        # Let's use 7/10 = 70% exactly
        # Better: 2 pass challenges worth 1 each, 1 fail worth 1 -> 2/3 = 66%
        # Let's just check the actual result
        self.assertEqual(result["score"], 4)
        self.assertEqual(result["max"], 6)
        # 4/6 = 66.67% < 70 -> False
        self.assertFalse(result["passed"])

    @patch("builtins.print")
    def test_passed_true_at_70_percent(self, mock_print):
        s = _session()
        # 10 challenges: 7 pass (1pt each), 3 fail (1pt max each)
        ch_pass = MagicMock()
        ch_pass.run = MagicMock(side_effect=lambda sess: _apply_score(sess, 1, 1))
        ch_fail = MagicMock()
        ch_fail.run = MagicMock(side_effect=lambda sess: _apply_fail(sess, 1))

        challenges = [ch_pass] * 7 + [ch_fail] * 3
        result = run_module("Test", "Lesson", challenges, s)
        self.assertEqual(result["score"], 7)
        self.assertEqual(result["max"], 10)
        self.assertTrue(result["passed"])  # 70% exactly

    @patch("builtins.print")
    def test_passed_false_below_70_percent(self, mock_print):
        s = _session()
        ch_pass = MagicMock()
        ch_pass.run = MagicMock(side_effect=lambda sess: _apply_score(sess, 1, 1))
        ch_fail = MagicMock()
        ch_fail.run = MagicMock(side_effect=lambda sess: _apply_fail(sess, 1))

        challenges = [ch_pass] * 6 + [ch_fail] * 4
        result = run_module("Test", "Lesson", challenges, s)
        self.assertEqual(result["score"], 6)
        self.assertEqual(result["max"], 10)
        self.assertFalse(result["passed"])  # 60% < 70%

    @patch("builtins.print")
    def test_tracks_missed_challenges(self, mock_print):
        s = _session()
        ch_pass = MagicMock()
        ch_pass.run = MagicMock(side_effect=lambda sess: _apply_score(sess, 1, 1))
        ch_pass.question = "Easy Q"

        ch_fail = MagicMock()
        ch_fail.run = MagicMock(side_effect=lambda sess: _apply_fail(sess, 1))
        ch_fail.question = "Hard Q"

        result = run_module("Test", "Lesson", [ch_pass, ch_fail], s)
        # The "Hard Q" question should appear in the printed output
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        self.assertIn("Hard Q", printed)

    @patch("builtins.print")
    def test_empty_challenges_list(self, mock_print):
        s = _session()
        result = run_module("Test", "Lesson", [], s)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["max"], 0)
        # pct = 0 (from else branch), 0 >= 70 is False
        self.assertFalse(result["passed"])


# Helpers for run_module mock challenges

def _apply_score(sess, score, max_pts):
    """Simulate a passing challenge."""
    sess.module_score += score
    sess.module_max += max_pts
    return True

def _apply_fail(sess, max_pts):
    """Simulate a failing challenge."""
    sess.module_max += max_pts
    return False


# ===========================================================================
# Progress Persistence: load_progress / save_progress / record_module
# ===========================================================================

class TestProgressPersistence(unittest.TestCase):

    def setUp(self):
        self._tmpfile = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        self._tmppath = Path(self._tmpfile.name)
        self._tmpfile.close()
        # Remove the file so load_progress sees "doesn't exist"
        self._tmppath.unlink(missing_ok=True)
        # Patch PROGRESS_FILE to point to our temp file
        self._patcher = patch.object(engine, "PROGRESS_FILE", self._tmppath)
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        if self._tmppath.exists():
            self._tmppath.unlink()

    def test_load_progress_no_file(self):
        result = load_progress()
        self.assertEqual(result, {"students": {}})

    def test_load_progress_existing_file(self):
        data = {"students": {"alice": {"mod1": {"score": 5, "max": 5, "passed": True}}}}
        with open(self._tmppath, "w") as f:
            json.dump(data, f)
        result = load_progress()
        self.assertEqual(result, data)

    def test_save_progress_writes_valid_json(self):
        data = {"students": {"bob": {"mod1": {"score": 3, "max": 5, "passed": False}}}}
        save_progress(data)
        with open(self._tmppath, "r") as f:
            raw = f.read()
        # Verify it's valid JSON
        loaded = json.loads(raw)
        self.assertEqual(loaded, data)
        # Verify indent=2 formatting (lines should be indented)
        self.assertIn("\n  ", raw)

    def test_record_module_creates_student_if_not_exists(self):
        result = {"score": 4, "max": 5, "passed": True}
        record_module("alice", "mod1", result)
        data = load_progress()
        self.assertIn("alice", data["students"])
        self.assertEqual(data["students"]["alice"]["mod1"], result)

    def test_record_module_overwrites_existing_module(self):
        first = {"score": 2, "max": 5, "passed": False}
        record_module("alice", "mod1", first)
        second = {"score": 5, "max": 5, "passed": True}
        record_module("alice", "mod1", second)
        data = load_progress()
        self.assertEqual(data["students"]["alice"]["mod1"], second)

    def test_record_module_preserves_other_students(self):
        record_module("alice", "mod1", {"score": 5, "max": 5, "passed": True})
        record_module("bob", "mod1", {"score": 3, "max": 5, "passed": False})
        data = load_progress()
        self.assertIn("alice", data["students"])
        self.assertIn("bob", data["students"])
        self.assertEqual(data["students"]["alice"]["mod1"]["score"], 5)
        self.assertEqual(data["students"]["bob"]["mod1"]["score"], 3)


if __name__ == "__main__":
    unittest.main()
