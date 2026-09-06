import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from authz import can_read, can_write  # noqa: E402

U = lambda role, pid="p1", uid="u1": {"uid": uid, "role": role, "program_id": pid}
R = lambda kind, pid="p1", owner=None, public=False: {"kind": kind, "program_id": pid, "owner_uid": owner, "public": public}


class Hidden(unittest.TestCase):
    def test_staff_cannot_read_other_program_board(self):
        self.assertFalse(can_read(U("staff", pid="p1"), R("board", pid="p2")))

    def test_staff_cannot_write_other_program_roster(self):
        self.assertFalse(can_write(U("staff", pid="p1"), R("roster", pid="p2")))

    def test_admin_scoped_to_program(self):
        self.assertTrue(can_write(U("admin", pid="p1"), R("board", pid="p1")))
        self.assertFalse(can_write(U("admin", pid="p1"), R("board", pid="p2")))

    def test_admin_writes_profile_in_program_staff_only_reads(self):
        self.assertTrue(can_write(U("admin", pid="p1"), R("profile", pid="p1", owner="x")))
        self.assertFalse(can_write(U("staff", pid="p1"), R("profile", pid="p1", owner="x")))
        self.assertTrue(can_read(U("staff", pid="p1"), R("profile", pid="p1", owner="x")))
        self.assertFalse(can_read(U("staff", pid="p1"), R("profile", pid="p2", owner="x")))

    def test_program_none_never_scoped(self):
        self.assertFalse(can_read(U("admin", pid=None), R("board", pid="p1")))
        self.assertFalse(can_write(U("admin", pid=None), R("board", pid=None)))

    def test_athlete_public_and_own_only(self):
        self.assertTrue(can_read(U("athlete", pid=None, uid="a1"), R("board", pid="p1", public=True)))
        self.assertFalse(can_read(U("athlete", pid=None, uid="a1"), R("profile", owner="a2")))
        self.assertFalse(can_write(U("athlete", pid=None, uid="a1"), R("board", public=True)))

    def test_unknown_role_and_kind_denied(self):
        self.assertFalse(can_read(U("guest"), R("board")))
        self.assertFalse(can_write(U("admin"), R("secret", pid="p1")))

    def test_super_admin_still_everything(self):
        self.assertTrue(can_read(U("super_admin", pid=None), R("profile", pid="p3", owner="z")))


if __name__ == "__main__":
    unittest.main()
