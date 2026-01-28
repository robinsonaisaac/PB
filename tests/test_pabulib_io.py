"""
Tests for Pabulib I/O utilities.
"""

import pytest
from fractions import Fraction
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pb.pabulib_io import parse_pabulib_file
from pb.ees import ees_with_outcome, cardinal_utility


class TestPabulibParsing:
    """Tests for parsing Pabulib .pb files."""
    
    @pytest.fixture
    def test_instance_path(self):
        """Path to the test instance."""
        return Path(__file__).parent.parent / "cli" / "test_instance.pb"
    
    def test_parse_test_instance(self, test_instance_path):
        """Parse the test instance file."""
        if not test_instance_path.exists():
            pytest.skip(f"Test instance not found: {test_instance_path}")
        
        election = parse_pabulib_file(str(test_instance_path))
        
        # Verify basic structure
        assert election.n > 0
        assert election.m > 0
        assert election.budget > 0
        
        # Verify projects have costs
        for pid, project in election.projects.items():
            assert project.cost > 0
    
    def test_parse_creates_valid_election(self, test_instance_path):
        """Parsed election can be used with EES."""
        if not test_instance_path.exists():
            pytest.skip(f"Test instance not found: {test_instance_path}")
        
        election = parse_pabulib_file(str(test_instance_path))
        
        # Should be able to run EES without errors
        outcome = ees_with_outcome(election, cardinal_utility)
        
        # Basic sanity checks
        assert outcome.total_cost <= election.budget
        assert all(pid in election.projects for pid in outcome.selected)


class TestPabulibRealInstance:
    """Test with the real Pabulib instance from the repo."""
    
    @pytest.fixture
    def real_instance_path(self):
        """Path to the actual test instance."""
        return Path(__file__).parent.parent / "cli" / "test_instance.pb"
    
    def test_real_instance_metadata(self, real_instance_path):
        """Verify metadata from test_instance.pb."""
        if not real_instance_path.exists():
            pytest.skip(f"Instance not found: {real_instance_path}")
        
        election = parse_pabulib_file(str(real_instance_path))
        
        # From the file: budget = 447000, num_projects = 9, num_votes = 1036
        assert election.budget == Fraction(447000)
        assert election.m == 9
        assert election.n == 1036
    
    def test_real_instance_projects(self, real_instance_path):
        """Verify projects from test_instance.pb."""
        if not real_instance_path.exists():
            pytest.skip(f"Instance not found: {real_instance_path}")
        
        election = parse_pabulib_file(str(real_instance_path))
        
        # Check some known project ids
        known_projects = ["W046AN", "W090AN", "W007AN"]
        for pid in known_projects:
            assert pid in election.projects
    
    def test_real_instance_ees_runs(self, real_instance_path):
        """EES runs on the real instance."""
        if not real_instance_path.exists():
            pytest.skip(f"Instance not found: {real_instance_path}")
        
        election = parse_pabulib_file(str(real_instance_path))
        outcome = ees_with_outcome(election, cardinal_utility)
        
        # Basic checks
        assert len(outcome.selected) > 0
        assert outcome.total_cost <= election.budget
        
        # Verify equal sharing invariant
        for pid in outcome.selected:
            payers = outcome.project_payers(pid)
            if payers:
                payments = [outcome.payment(v, pid) for v in payers]
                assert all(p == payments[0] for p in payments)

