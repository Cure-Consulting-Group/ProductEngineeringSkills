import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from authz import can_read, can_write  # noqa: E402

U = lambda role, pid="p1", uid="u1": {"uid": uid, "role": role, "program_id": pid}
R = lambda kind, pid="p1", owner=None, public=False: {"kind": kind, "program_id": pid, "owner_uid": owner, "public": public}


class Visible(unittest.TestCase):
    def test_staff_reads_own_program_board(self):
        self.assertTrue(can_read(U("staff"), R("board")))

    def test_athlete_reads_own_profile(self):
        self.assertTrue(can_read(U("athlete", pid=None, uid="a1"), R("profile", owner="a1")))

    def test_super_admin_writes_anything(self):
        self.assertTrue(can_write(U("super_admin", pid=None), R("board", pid="p9")))


if __name__ == "__main__":
    unittest.main()
