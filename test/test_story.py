import sys
from pathlib import Path
import pytest

import numpy as np

etabs_api_path = Path(__file__).parent.parent
sys.path.insert(0, str(etabs_api_path))

from shayesteh import etabs, open_etabs_file

@open_etabs_file('shayesteh.EDB')
def test_get_heights():
    hx, hy = etabs.story.get_heights()
    h = 18.68
    assert hx == h
    assert hy == h

@open_etabs_file('shayesteh.EDB')
def test_get_top_bot_stories():
    bot_story_x, top_story_x, bot_story_y, top_story_y = etabs.story.get_top_bot_stories()
    assert bot_story_x == bot_story_y == 'BASE'
    assert top_story_x == top_story_y == 'STORY5'

@open_etabs_file('shayesteh.EDB')
def test_get_top_bot_levels():
    bot_level_x, top_level_x, bot_level_y, top_level_y = etabs.story.get_top_bot_levels()
    assert bot_level_x == bot_level_y == 0
    assert top_level_x == top_level_y == 18.68

@open_etabs_file('shayesteh.EDB')
def test_get_no_of_stories():
    nx, ny = etabs.story.get_no_of_stories()
    assert nx == ny == 5
    nx, ny = etabs.story.get_no_of_stories(0, 15.84, 0, 15.84)
    assert nx == ny == 4

@open_etabs_file('shayesteh.EDB')
def test_get_story_boundbox():
    geo = etabs.story.get_story_boundbox('STORY4')
    assert pytest.approx(geo, abs=.1) == (-118.1, 0, 1769, 1467.5)
    geo = etabs.story.get_story_boundbox('STORY5')
    assert pytest.approx(geo, abs=.1) == (653, 0, 1469, 500)

@open_etabs_file('shayesteh.EDB')
def test_get_stories_boundbox():
    story_bb = etabs.story.get_stories_boundbox()
    assert len(story_bb) == 5
    bb = story_bb['STORY4']
    assert pytest.approx(bb, abs=.1) == (-118.1, 0, 1769, 1467.5)
    bb = story_bb['STORY5']
    assert pytest.approx(bb, abs=.1) == (653, 0, 1469, 500)

@open_etabs_file('shayesteh.EDB')
def test_get_stories_length():
    story_length = etabs.story.get_stories_length()
    assert len(story_length) == 5
    length = story_length['STORY4']
    assert pytest.approx(length, abs=.1) == (1887.1, 1467.5)
    length = story_length['STORY5']
    assert pytest.approx(length, abs=.1) == (816, 500)

@open_etabs_file('shayesteh.EDB')
def test_get_story_diaphragms():
    diaph_set = set()
    for story in etabs.SapModel.Story.GetNameList()[1]:
        diaph = etabs.story.get_story_diaphragms(story).pop()
        diaph_set.add(diaph)
    assert diaph_set == {'D1'}

@open_etabs_file('shayesteh.EDB')
def test_add_points_in_center_of_rigidity_and_assign_diph():
    story_point_in_center_of_rigidity = etabs.story.add_points_in_center_of_rigidity_and_assign_diph()
    assert len(story_point_in_center_of_rigidity) == 5

@open_etabs_file('shayesteh.EDB')
def test_get_stories_diaphragms():
    story_diaphs = etabs.story.get_stories_diaphragms()
    assert story_diaphs == {
        'STORY5': ['D1'],
        'STORY4': ['D1'],
        'STORY3': ['D1'],
        'STORY2': ['D1'],
        'STORY1': ['D1'],
    }

@open_etabs_file('shayesteh.EDB')
def test_storyname_and_levels():
    etabs.set_current_unit('N', 'mm')
    story_levels = etabs.story.storyname_and_levels()
    assert story_levels == pytest.approx({
                    'BASE': 0.0, 
                    'STORY1': 5220.0, 
                    'STORY2': 8640.0, 
                    'STORY3': 12060.0, 
                    'STORY4': 15480.0, 
                    'STORY5': 18680.0,
                    })

@open_etabs_file('shayesteh.EDB')
def test_get_sorted_story_name():
    stories = etabs.story.get_sorted_story_name(reverse=True, include_base=True)
    assert stories == ['STORY5', 'STORY4', 'STORY3', 'STORY2', 'STORY1', 'BASE']
    stories = etabs.story.get_sorted_story_name(reverse=True, include_base=False)
    assert stories == ['STORY5', 'STORY4', 'STORY3', 'STORY2', 'STORY1']
    stories = etabs.story.get_sorted_story_name(reverse=False, include_base=False)
    assert stories == ['STORY1', 'STORY2', 'STORY3', 'STORY4', 'STORY5']
    stories = etabs.story.get_sorted_story_name(reverse=False, include_base=True)
    assert stories == ['BASE', 'STORY1', 'STORY2', 'STORY3', 'STORY4', 'STORY5']

@open_etabs_file('shayesteh.EDB')
def test_get_sorted_story_and_levels():
    l = etabs.story.get_sorted_story_and_levels(reverse=True, include_base=True)
    assert [i[0] for i in l] == ['STORY5', 'STORY4', 'STORY3', 'STORY2', 'STORY1', 'BASE']
    l = etabs.story.get_sorted_story_and_levels(reverse=True, include_base=False)
    assert [i[0] for i in l] == ['STORY5', 'STORY4', 'STORY3', 'STORY2', 'STORY1']
    l = etabs.story.get_sorted_story_and_levels(reverse=False, include_base=False)
    assert [i[0] for i in l] == ['STORY1', 'STORY2', 'STORY3', 'STORY4', 'STORY5']
    l = etabs.story.get_sorted_story_and_levels(reverse=False, include_base=True)
    assert [i[0] for i in l] == ['BASE', 'STORY1', 'STORY2', 'STORY3', 'STORY4', 'STORY5']

@open_etabs_file('shayesteh.EDB')
def test_get_diaphragm_force():
    diaphragm_forces = etabs.story.get_diaphragm_force(loadcases=('QX', 'QY'))
    assert len(diaphragm_forces) == 2
    assert diaphragm_forces['QX']['STORY5'] == (0, 0)
    np.testing.assert_almost_equal(diaphragm_forces['QX']['STORY4'], [-36707.346, 0], decimal=0)

@open_etabs_file('shayesteh.EDB')
def test_get_diaphragm_earthquakes_factor():
    ai = 0.35
    diaphragm_forces = etabs.story.get_diaphragm_earthquakes_factor(
        x_names=('QX',),
        y_names=('QY',),
        ai=ai
        )
    print(diaphragm_forces)
    assert len(diaphragm_forces) == 2
    np.testing.assert_almost_equal(diaphragm_forces['QX']['STORY5'], ai / 2, decimal=3)
    np.testing.assert_almost_equal(diaphragm_forces['QY']['STORY5'], ai / 2, decimal=3)

@open_etabs_file('shayesteh.EDB')
def test_create_files_diaphragm_applied_forces():
    d = {}
    d['ex_combobox'] = 'QX'
    d['exn_combobox'] = 'QXN'
    d['exp_combobox'] = 'QXP'
    d['ey_combobox'] = 'QY'
    d['eyn_combobox'] = 'QYN'
    d['eyp_combobox'] = 'QYP'
    etabs.story.create_files_diaphragm_applied_forces(
        stories=["STORY4"],
        d = d,
        )
    _, new_filename = etabs.get_new_filename_in_folder_and_add_name('diaphragm_forces', "STORY4")
    etabs.SapModel.File.OpenFile(str(new_filename))
    table_key = 'Load Pattern Definitions - Auto Seismic - User Coefficient'
    df = etabs.database.read(table_key, to_dataframe=True)
    new_data = ['STORY4', 'STORY3', '1']
    ret = df.loc[df.Name.isin(("QX", "QXN", "QXP", "QY", "QYN", "QYP")), ['TopStory', 'BotStory', 'K']] == new_data
    assert ret.all().all()
    for lp in ('QX', 'QXN', 'QXP', 'QY', 'QYN', 'QYP'):
        assert etabs.SapModel.LoadPatterns.GetLoadType(lp)[0] == 5


if __name__ == "__main__":
    test_create_files_diaphragm_applied_forces()