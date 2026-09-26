"""Regression cases from independent review on 2026-09-26."""
import tempfile
import unittest
from pathlib import Path
from src.checkers import check_img_alt, check_label_for, check_broken_links
from src.compare import compare_reports
from src.schema import make_report

class LabelRegressionTests(unittest.TestCase):
    def test_wrapping_label_names_field(self):
        self.assertEqual(check_label_for('<label>Name <input id="name"></label>', 'index.html'), [])
    def test_empty_explicit_label_is_reported(self):
        self.assertEqual(len(check_label_for('<label for="x"> </label><input id="x">', 'index.html')), 1)
    def test_empty_aria_label_is_reported(self):
        self.assertEqual(len(check_label_for('<input aria-label="  ">', 'index.html')), 1)
    def test_dangling_labelledby_is_reported(self):
        self.assertEqual(len(check_label_for('<input aria-labelledby="missing">', 'index.html')), 1)
    def test_text_labelledby_is_accepted(self):
        self.assertEqual(check_label_for('<span id="n">Name</span><input aria-labelledby="n">', 'index.html'), [])
    def test_select_and_textarea_are_checked(self):
        self.assertEqual(len(check_label_for('<select></select><textarea></textarea>', 'index.html')), 2)
    def test_input_type_is_case_insensitive(self):
        self.assertEqual(check_label_for('<input type="HIDDEN"><input type="SUBMIT">', 'index.html'), [])
    def test_mismatched_wrapping_label_is_not_accepted(self):
        self.assertEqual(len(check_label_for('<label for="other">Name<input id="x"></label>', 'index.html')), 1)
    def test_script_text_does_not_supply_a_name(self):
        self.assertEqual(len(check_label_for('<label><script>var a=1</script><input></label>', 'index.html')), 1)

    def test_title_name_is_accepted(self):
        self.assertEqual(check_label_for('<input title="Search">', 'index.html'), [])
    def test_image_input_alt_name_is_accepted(self):
        self.assertEqual(check_label_for('<input type="image" alt="Search">', 'index.html'), [])
    def test_image_in_label_supplies_name(self):
        self.assertEqual(check_label_for('<label><img alt="Name"><input></label>', 'index.html'), [])
    def test_hidden_label_text_does_not_supply_name(self):
        self.assertEqual(len(check_label_for('<label><span hidden>Name</span><input></label>', 'index.html')), 1)

class LinkRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/'about us.html').write_text('About')
        self.page=str(self.root/'index.html')
    def tearDown(self):
        self.tmp.cleanup()
    def test_encoded_file_query_and_fragment(self):
        self.assertEqual(check_broken_links('<a href="about%20us.html?ref=menu#team">About</a>', self.page), [])
    def test_protocol_relative_is_external(self):
        self.assertEqual(check_broken_links('<a href="//example.org/path">External</a>', self.page), [])
    def test_schemes_are_not_local_files(self):
        self.assertEqual(check_broken_links('<a href="HTTPS://example.org">Web</a><a href="sms:123">SMS</a>', self.page), [])
    def test_parent_relative_file_resolves(self):
        (self.root/'nested').mkdir()
        self.assertEqual(check_broken_links('<a href="../about%20us.html">About</a>', str(self.root/'nested/index.html')), [])
    def test_missing_file_is_still_reported(self):
        self.assertEqual(len(check_broken_links('<a href="missing.html?a=1#x">Missing</a>', self.page)), 1)
    def test_root_relative_is_out_of_single_file_scope(self):
        self.assertEqual(check_broken_links('<a href="/about">About</a>', self.page), [])

    def test_external_base_url_is_out_of_local_scope(self):
        self.assertEqual(check_broken_links('<base href="https://example.org"><a href="remote.html">Remote</a>', self.page), [])

class InstanceComparisonTests(unittest.TestCase):
    def compare(self, before, after):
        return compare_reports(make_report(check_img_alt(before, 'index.html'), 'index.html'), make_report(check_img_alt(after, 'index.html'), 'index.html'))
    def test_fixing_one_of_two_images_preserves_other(self):
        c=self.compare('<img src="a"><img src="b">', '<img src="a" alt="A"><img src="b">')
        self.assertEqual(c['comparison_summary'], {'fixed':1,'still_open':1,'regressed':0})
        self.assertIn('b', c['findings'][0]['evidence'])
    def test_identical_instances_are_counted(self):
        c=self.compare('<img src="a"><img src="a">', '<img src="a" alt="A"><img src="a">')
        self.assertEqual(c['comparison_summary'], {'fixed':1,'still_open':1,'regressed':0})
    def test_line_shift_is_not_a_new_issue(self):
        c=self.compare('<img src="a">', '\n\n<img src="a">')
        self.assertEqual(c['comparison_summary'], {'fixed':0,'still_open':1,'regressed':0})
    def test_new_instance_of_same_rule_is_regressed(self):
        c=self.compare('<img src="a">', '<img src="a"><img src="b">')
        self.assertEqual(c['comparison_summary'], {'fixed':0,'still_open':1,'regressed':1})
    def test_replacing_instance_is_not_a_verified_fix_only(self):
        c=self.compare('<img src="a">', '<img src="b">')
        self.assertEqual(c['comparison_summary'], {'fixed':1,'still_open':0,'regressed':1})

    def test_legacy_before_matches_new_after(self):
        before=make_report(check_img_alt('<img src="a">', 'index.html'),'index.html')
        before['findings'][0].pop('fingerprint')
        after=make_report(check_img_alt('\n<img src="a">', 'index.html'),'index.html')
        self.assertEqual(compare_reports(before,after)['comparison_summary'], {'fixed':0,'still_open':1,'regressed':0})
    def test_legacy_after_matches_new_before(self):
        before=make_report(check_img_alt('<img src="a"><img src="b">', 'index.html'),'index.html')
        after=make_report(check_img_alt('<img src="b">', 'index.html'),'index.html')
        after['findings'][0].pop('fingerprint')
        self.assertEqual(compare_reports(before,after)['comparison_summary'], {'fixed':1,'still_open':1,'regressed':0})

    def test_unverified_state_is_not_dropped(self):
        r=make_report(check_img_alt('<img src="a">','index.html'),'index.html')
        r['findings'][0]['state']='unverified'
        c=compare_reports(r,r)
        self.assertEqual(len(c['findings']),1)
        self.assertEqual(c['findings'][0]['state'],'unverified')
        self.assertEqual(c['comparison_summary']['still_open'],1)
    def test_href_without_value_does_not_crash(self):
        self.assertEqual(check_img_alt('<img src="decorative.png" alt>','index.html'),[])
        self.assertEqual(check_broken_links('<a href>Unknown</a>','index.html'),[])
