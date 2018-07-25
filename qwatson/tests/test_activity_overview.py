# -*- coding: utf-8 -*-

# Copyright © 2018 Jean-Sébastien Gosselin
# https://github.com/jnsebgosselin/qwatson
#
# This file is part of QWatson.
# Licensed under the terms of the GNU General Public License.

# ---- Standard imports

import os
import os.path as osp
import json

# ---- Third party imports

import pytest
from PyQt5.QtCore import Qt

# ---- Local imports

from qwatson.watson_ext.watsonextends import Frames
from qwatson.mainwindow import QWatson
from qwatson.utils.dates import local_arrow_from_tuple
from qwatson.utils.fileio import delete_folder_recursively
from qwatson.utils.dates import qdatetime_from_str
from qwatson.models.delegates import DateTimeDelegate


# ---- Fixtures and utilities


@pytest.fixture(scope="module")
def now():
    return local_arrow_from_tuple((2018, 6, 17, 23, 59, 0))


@pytest.fixture(scope="module")
def span(now):
    return now.floor('week').span('week')


@pytest.fixture(scope="module")
def appdir(now, span):
    # We do not use the tmpdir_factory fixture because we use the files
    # produces by the tests to test QWatson locally

    appdir = osp.join(osp.dirname(__file__), 'appdir', 'activity_overview')

    delete_folder_recursively(appdir)
    if not osp.exists(appdir):
        os.makedirs(appdir)

    # Create the frames file.

    frames = Frames()
    i = 1
    while True:
        frame = frames.add(project='test_overview',
                           start=span[0].shift(hours=i*6).timestamp,
                           stop=span[0].shift(hours=(i+1)*6).timestamp,
                           message='activity #%s' % (i//2),
                           updated_at=now
                           )
        if frame.stop >= span[1]:
            break
        i += 2

    with open(osp.join(appdir, 'frames'), 'w') as f:
        f.write(json.dumps(frames.dump(), indent=1, ensure_ascii=False))

    return appdir


@pytest.fixture
def overview_creator(qtbot, mocker, appdir, now):
    mocker.patch('arrow.now', return_value=now)
    qwatson = QWatson(config_dir=appdir)

    qtbot.addWidget(qwatson)
    qwatson.show()
    qtbot.waitForWindowShown(qwatson)

    qtbot.addWidget(qwatson.overview_widg)
    qtbot.mouseClick(qwatson.btn_report, Qt.LeftButton)
    qtbot.waitForWindowShown(qwatson.overview_widg)

    return qwatson.overview_widg, qtbot, mocker


# ---- Tests


def test_overview_init(overview_creator, span):
    """Test that the overview is initialized correctly."""
    overview, qtbot, mocker = overview_creator

    assert overview.isVisible()
    assert overview.table_widg.total_seconds == 7*(2*6)*60*60
    assert len(overview.table_widg.tables) == 7
    assert overview.table_widg.last_focused_table is None
    assert overview.table_widg.date_span == span

    # Assert that the overview table is showing the right number of activities.

    row_counts = [table.rowCount() for table in overview.table_widg.tables]
    assert row_counts == [2, 2, 2, 2, 2, 2, 2]


def test_overview_row_selection(overview_creator):
    """
    Test that table and row selection is working as expected.
    """
    overview, qtbot, mocker = overview_creator
    tables = overview.table_widg.tables

    # Mouse click on the second row of the second table.

    index = tables[1].view.proxy_model.index(1, 0)
    visual_rect = tables[1].view.visualRect(index)

    qtbot.mouseClick(
        tables[1].view.viewport(), Qt.LeftButton, pos=visual_rect.center())

    # Assert that all but one table have a row and a frame selected.

    assert overview.table_widg.last_focused_table == tables[1]
    for table in tables:
        if table != overview.table_widg.last_focused_table:
            assert table.get_selected_row() is None
            assert table.get_selected_frame_index() is None
        else:
            assert table.get_selected_row() == 1
            assert table.get_selected_frame_index() == 2 + 2 - 1

    # Mouse click on the first row of the second table.

    index = tables[2].view.proxy_model.index(2, 0)
    visual_rect = tables[2].view.visualRect(index)

    qtbot.mouseClick(
        tables[2].view.viewport(), Qt.LeftButton, pos=visual_rect.center())

    assert overview.table_widg.last_focused_table == tables[2]

    # Assert that all tables but 2 have no selected row and frame.

    for table in tables:
        if table != overview.table_widg.last_focused_table:
            assert table.get_selected_row() is None
            assert table.get_selected_frame_index() is None
        else:
            assert table.get_selected_row() == 0
            assert table.get_selected_frame_index() == 2 + 2 + 1 - 1


def test_mouse_hovered_row(overview_creator):
    """
    Test that the highlighting of mouse hovered row is working as expected.
    """
    overview, qtbot, mocker = overview_creator
    tables = overview.table_widg.tables

    # Mouse hover the second row of the second table.

    index = tables[1].view.proxy_model.index(1, 0)
    visual_rect = tables[1].view.visualRect(index)

    qtbot.mouseMove(tables[1].view.viewport(), pos=visual_rect.center())
    tables[1].view.itemEnterEvent(index)
    assert tables[1].view._hovered_row == 1

    # Mouse hover the first row of the fourth table and simulate a change of
    # value of the scrollbar. Assert that the _hovered_row of the second
    # table is now None and that the  _hovered_row of the fourth table is 0.

    index = tables[4].view.proxy_model.index(0, 0)
    visual_rect = tables[4].view.visualRect(index)

    qtbot.mouseMove(tables[4].view.viewport(), pos=visual_rect.center())
    overview.table_widg.srollbar_value_changed(
        overview.table_widg.scrollarea.verticalScrollBar().value())

    assert tables[1].view._hovered_row is None
    assert tables[4].view._hovered_row == 0


def test_daterange_navigation(overview_creator, span):
    """
    Test that the widget to change the datespan of the activity overview is
    working as expected.
    """
    overview, qtbot, mocker = overview_creator
    assert not overview.date_range_nav.btn_next.isEnabled()

    # Move back one week.

    qtbot.mouseClick(overview.date_range_nav.btn_prev, Qt.LeftButton)
    new_span = (span[0].shift(weeks=-1), span[1].shift(weeks=-1))
    assert overview.table_widg.date_span == new_span
    assert overview.date_range_nav.btn_next.isEnabled()

    # Move back two additional weeks.

    qtbot.mouseClick(overview.date_range_nav.btn_prev, Qt.LeftButton)
    qtbot.mouseClick(overview.date_range_nav.btn_prev, Qt.LeftButton)
    new_span = (new_span[0].shift(weeks=-2), new_span[1].shift(weeks=-2))
    assert overview.table_widg.date_span == new_span
    assert overview.date_range_nav.btn_next.isEnabled()

    # Move forth one week.

    qtbot.mouseClick(overview.date_range_nav.btn_next, Qt.LeftButton)
    new_span = (new_span[0].shift(weeks=1), new_span[1].shift(weeks=1))
    assert overview.table_widg.date_span == new_span
    assert overview.date_range_nav.btn_next.isEnabled()

    # Go back home.

    qtbot.mouseClick(overview.date_range_nav.btn_home, Qt.LeftButton)
    assert overview.table_widg.date_span == span
    assert not overview.date_range_nav.btn_next.isEnabled()


def test_selected_row_is_cleared_when_navigating(overview_creator):
    """
    Test that the selected row is cleared when changing the date span of the
    overview table with the date range navigator widget.
    """
    overview, qtbot, mocker = overview_creator
    table = overview.table_widg.tables[1]

    # Select the second row of the second table.

    visual_rect = table.view.visualRect(table.view.proxy_model.index(1, 0))
    qtbot.mouseClick(
        table.view.viewport(), Qt.LeftButton, pos=visual_rect.center())
    assert table.get_selected_row() == 1
    assert overview.table_widg.last_focused_table == table

    # Move back and forth one week in the date range navigation widget.

    qtbot.mouseClick(overview.date_range_nav.btn_prev, Qt.LeftButton)

    # Assert that the selected row was cleared as expected.

    assert overview.table_widg.last_focused_table is None
    for table in overview.table_widg.tables:
        assert table.get_selected_row() is None


# ---- Test Edits


def test_edit_start_datetime(overview_creator):
    """Test editing the start date in the activity overview table."""
    overview, qtbot, mocker = overview_creator

    # Edit the start date of the first frame in the first table.

    table = overview.table_widg.tables[0]
    index = table.view.proxy_model.index(0, 0)
    delegate = table.view.itemDelegate(index)
    assert isinstance(delegate, DateTimeDelegate)

    # Check that the start value is contraint by the stop value of the frame.

    table.view.edit(index)
    assert delegate.editor.isVisible()
    assert (delegate.editor.dateTime().toString("yyyy-MM-dd hh:mm") ==
            '2018-06-11 06:00')

    delegate.editor.setDateTime(qdatetime_from_str('2018-06-11 15:23'))
    with qtbot.waitSignal(table.view.proxy_model.sig_sourcemodel_changed):
        qtbot.keyPress(delegate.editor, Qt.Key_Enter)

    assert (overview.model.client.frames[0].start.format('YYYY-MM-DD HH:mm') ==
            '2018-06-11 12:00')

    # Check that the stat is changed correctly when a valid value is
    # provided.

    table.view.edit(index)
    assert delegate.editor.isVisible()
    assert (delegate.editor.dateTime().toString("yyyy-MM-dd hh:mm") ==
            '2018-06-11 12:00')

    delegate.editor.setDateTime(qdatetime_from_str('2018-06-11 07:16'))
    with qtbot.waitSignal(table.view.proxy_model.sig_sourcemodel_changed):
        qtbot.keyPress(delegate.editor, Qt.Key_Enter)

    assert (overview.model.client.frames[0].start.format('YYYY-MM-DD HH:mm') ==
            '2018-06-11 07:16')


def test_edit_stop_datetime(overview_creator):
    """Test editing the stop date in the activity overview table."""
    overview, qtbot, mocker = overview_creator
    overview.show()
    qtbot.waitForWindowShown(overview)

    # Edit the stop date of the first frame of the third table

    table = overview.table_widg.tables[2]
    index = table.view.proxy_model.index(0, 1)
    delegate = table.view.itemDelegate(table.view.proxy_model.index(0, 1))
    assert isinstance(delegate, DateTimeDelegate)

    # Check that the stop value is constraint by the start value of the frame.

    table.view.edit(index)
    assert delegate.editor.isVisible()
    assert (delegate.editor.dateTime().toString("yyyy-MM-dd hh:mm") ==
            '2018-06-13 12:00')

    delegate.editor.setDateTime(qdatetime_from_str('2018-06-13 03:00'))
    with qtbot.waitSignal(table.view.proxy_model.sig_sourcemodel_changed):
        qtbot.keyPress(delegate.editor, Qt.Key_Enter)

    assert (overview.model.client.frames[4].stop.format('YYYY-MM-DD HH:mm') ==
            '2018-06-13 06:00')

    # Check that the stop value is contraint by the start value of the
    # next frame.

    table.view.edit(index)
    assert delegate.editor.isVisible()
    assert (delegate.editor.dateTime().toString("yyyy-MM-dd hh:mm") ==
            '2018-06-13 06:00')

    delegate.editor.setDateTime(qdatetime_from_str('2018-06-13 21:45'))
    with qtbot.waitSignal(table.view.proxy_model.sig_sourcemodel_changed):
        qtbot.keyPress(delegate.editor, Qt.Key_Enter)

    assert (overview.model.client.frames[4].stop.format('YYYY-MM-DD HH:mm') ==
            '2018-06-13 18:00')


if __name__ == "__main__":
    pytest.main(['-x', os.path.basename(__file__), '-v', '-rw'])