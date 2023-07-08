# discord @mr.smoothy#5824

# ba_meta require api 8

from __future__ import annotations
import copy
import time
from typing import TYPE_CHECKING

import babase
import bauiv1 as bui
import bascenev1 as bs
import _bascenev1 as _bs
import time
import threading
from enum import Enum
from dataclasses import dataclass
if TYPE_CHECKING:
    from typing import Any, Optional, Dict, List, Tuple, Type
    import bascenev1 as bs
    from bauiv1lib.gather import GatherWindow

from bauiv1lib.confirm import ConfirmWindow

import bauiv1lib.mainmenu as bastd_ui_mainmenu

connect = bs.connect_to_party
disconnect = bs.disconnect_from_host

server = []

ip_add = "private"
p_port = 44444
p_name = "nothing here"


def newconnect_to_party(address, port=43210, print_progress=False):
    global ip_add
    global p_port
    dd = _bs.get_connection_to_host_info()
    if (dd != {}):
        _bs.disconnect_from_host()

        ip_add = address
        p_port = port
        connect(address, port, print_progress)
    else:

        ip_add = address
        p_port = port
        # print(ip_add,p_port)
        connect(ip_add, port, print_progress)


def newdisconnect_from_host():
    try:
        name = _bs.get_connection_to_host_info()['name']
        global server
        global ip_add
        global p_port
        pojo = {"name": name, "ip": ip_add, "port": p_port}
        if pojo not in server:
            server.insert(0, pojo)
            server = server[:3]
    except:
        pass
    disconnect()


def printip():
    bs.screenmessage("ip address is"+ip_add)


def new_refresh_in_game(
        self, positions: List[Tuple[float, float,
                                    float]]) -> Tuple[float, float, float]:
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    custom_menu_entries: List[Dict[str, Any]] = []
    session = _bs.get_foreground_host_session()
    if session is not None:
        try:
            custom_menu_entries = session.get_custom_menu_entries()
            for cme in custom_menu_entries:
                if (not isinstance(cme, dict) or 'label' not in cme
                        or not isinstance(cme['label'], (str, bs.Lstr))
                        or 'call' not in cme or not callable(cme['call'])):
                    raise ValueError('invalid custom menu entry: ' +
                                     str(cme))
        except Exception:
            custom_menu_entries = []
            babase.print_exception(
                f'Error getting custom menu entries for {session}')
    self._width = 250.0
    self._height = 250.0 if self._input_player else 180.0
    if (self._is_demo or self._is_arcade) and self._input_player:
        self._height -= 40
    if not self._have_settings_button:
        self._height -= 50
    if self._connected_to_remote_player:
        # In this case we have a leave *and* a disconnect button.
        self._height += 50
    self._height += 50 * (len(custom_menu_entries))
    uiscale = bui.app.ui_v1.uiscale
    bui.containerwidget(
        edit=self._root_widget,
        size=(self._width*2, self._height),
        scale=(2.15 if uiscale is bui.UIScale.SMALL else
               1.6 if uiscale is bui.UIScale.MEDIUM else 1.0))
    h = 125.0
    v = (self._height - 80.0 if self._input_player else self._height - 60)
    h_offset = 0
    d_h_offset = 0
    v_offset = -50
    for _i in range(6 + len(custom_menu_entries)):
        positions.append((h, v, 1.0))
        v += v_offset
        h += h_offset
        h_offset += d_h_offset
    self._start_button = None
    bui.app.pause()
    h, v, scale = positions[self._p_index]
    bui.textwidget(
        parent=self._root_widget,
        draw_controller=None,
        text="IP: "+ip_add+"  PORT: "+str(p_port),
        position=(h+self._button_width-80, v+60),
        h_align='center',
        v_align='center',
        size=(20, 60),
        scale=0.6)
    v_h = v

    global server

    def con(address, port):
        global ip_add
        global p_port
        if (address == ip_add and port == p_port):
            self._resume()
        else:
            _bs.disconnect_from_host()
            _bs.connect_to_party(address, port)
    if len(server) == 0:
        bui.textwidget(
            parent=self._root_widget,
            draw_controller=None,
            text="Nothing in \n recents",
            position=(h + self._button_width * scale, v-30),
            h_align='center',
            v_align='center',
            size=(20, 60),
            scale=1)
    for ser in server:
        self._server_button = bui.buttonwidget(
            color=(0.8, 0, 1),
            parent=self._root_widget,
            position=(h + self._button_width * scale - 80, v_h),
            size=(self._button_width, self._button_height),
            scale=scale,
            autoselect=self._use_autoselect,
            label=ser["name"][0:22],

            on_activate_call=bs.Call(con, ser["ip"], ser["port"]))
        v_h = v_h-50

    # Player name if applicable.
    if self._input_player:
        player_name = self._input_player.getname()
        h, v, scale = positions[self._p_index]
        v += 35
        bui.textwidget(parent=self._root_widget,
                       position=(h - self._button_width / 2, v),
                       size=(self._button_width, self._button_height),
                       color=(1, 1, 1, 0.5),
                       scale=0.7,
                       h_align='center',
                       text=bs.Lstr(value=player_name))
    else:
        player_name = ''
    h, v, scale = positions[self._p_index]
    self._p_index += 1
    btn = bui.buttonwidget(parent=self._root_widget,
                           position=(h - self._button_width / 2, v),
                           size=(self._button_width, self._button_height),
                           scale=scale,
                           label=bs.Lstr(resource=self._r + '.resumeText'),
                           autoselect=self._use_autoselect,
                           on_activate_call=self._resume)
    bui.containerwidget(edit=self._root_widget, cancel_button=btn)

    # Add any custom options defined by the current game.
    for entry in custom_menu_entries:
        h, v, scale = positions[self._p_index]
        self._p_index += 1

        # Ask the entry whether we should resume when we call
        # it (defaults to true).
        resume = bool(entry.get('resume_on_call', True))

        if resume:
            call = bs.Call(self._resume_and_call, entry['call'])
        else:
            call = bs.Call(entry['call'], bs.WeakCall(self._resume))

        bui.buttonwidget(parent=self._root_widget,
                         position=(h - self._button_width / 2, v),
                         size=(self._button_width, self._button_height),
                         scale=scale,
                         on_activate_call=call,
                         label=entry['label'],
                         autoselect=self._use_autoselect)
    # Add a 'leave' button if the menu-owner has a player.
    if ((self._input_player or self._connected_to_remote_player)
            and not (self._is_demo or self._is_arcade)):
        h, v, scale = positions[self._p_index]
        self._p_index += 1
        btn = bui.buttonwidget(parent=self._root_widget,
                               position=(h - self._button_width / 2, v),
                               size=(self._button_width,
                                     self._button_height),
                               scale=scale,
                               on_activate_call=self._leave,
                               label='',
                               autoselect=self._use_autoselect)

        if (player_name != '' and player_name[0] != '<'
                and player_name[-1] != '>'):
            txt = bs.Lstr(resource=self._r + '.justPlayerText',
                          subs=[('${NAME}', player_name)])
        else:
            txt = bs.Lstr(value=player_name)
        bui.textwidget(parent=self._root_widget,
                       position=(h, v + self._button_height *
                                 (0.64 if player_name != '' else 0.5)),
                       size=(0, 0),
                       text=bs.Lstr(resource=self._r + '.leaveGameText'),
                       scale=(0.83 if player_name != '' else 1.0),
                       color=(0.75, 1.0, 0.7),
                       h_align='center',
                       v_align='center',
                       draw_controller=btn,
                       maxwidth=self._button_width * 0.9)
        bui.textwidget(parent=self._root_widget,
                       position=(h, v + self._button_height * 0.27),
                       size=(0, 0),
                       text=txt,
                       color=(0.75, 1.0, 0.7),
                       h_align='center',
                       v_align='center',
                       draw_controller=btn,
                       scale=0.45,
                       maxwidth=self._button_width * 0.9)
    return h, v, scale


def new_refresh(self) -> None:
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    global server
    print(server)
    from bauiv1lib.confirm import QuitWindow
    from bauiv1lib.store.button import StoreButton
    import bascenev1 as bs
    import _bascenev1 as _bs
    import bauiv1 as bui
    import _baplus
    # Clear everything that was there.
    children = self._root_widget.get_children()
    for child in children:
        child.delete()

    self._tdelay = 0.0
    self._t_delay_inc = 0.0
    self._t_delay_play = 0.0
    self._button_width = 200.0
    self._button_height = 45.0

    self._r = 'mainMenu'

    assert bs.app.classic is not None
    app = bs.app.classic
    self._have_quit_button = (bui.app.ui_v1.uiscale is bui.UIScale.LARGE
                              or (app.platform == 'windows'
                                  and app.subplatform == 'oculus'))

    self._have_store_button = not self._in_game

    self._have_settings_button = (
        (not self._in_game or not bui.app.toolbar_test)
        and not (self._is_demo or self._is_arcade or self._is_iircade))

    self._input_device = input_device = _bs.get_ui_input_device()
    self._input_player = input_device.player if input_device else None
    self._connected_to_remote_player = (
        input_device.is_attached_to_player()
        if input_device else False)

    positions: List[Tuple[float, float, float]] = []
    self._p_index = 0

    if self._in_game:
        h, v, scale = self._refresh_in_game(positions)
        print("refreshing in GAME", ip_add)
        # btn = bui.buttonwidget(parent=self._root_widget,
        #                   position=(80,270),
        #                   size=(100, 90),
        #                   scale=1.2,
        #                   label=ip_add,
        #                   autoselect=None,
        #                   on_activate_call=printip)
        bui.textwidget(
            parent=self._root_widget,
            draw_controller=None,
            text="IP: "+ip_add+"  PORT: "+str(p_port),
            position=(150, 270),
            h_align='center',
            v_align='center',
            size=(20, 60),
            scale=1)
        self._server_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(h * 3.2 + 20 - self._button_width * scale, v),
            size=(self._button_width, self._button_height),
            scale=scale,
            autoselect=self._use_autoselect,
            label=bs.Lstr(resource=self._r + '.settingsText'),
            transition_delay=self._tdelay,
            on_activate_call=self._settings)
        self._server_button2 = bui.buttonwidget(
            parent=self._root_widget,
            position=(h * 3.2 + 20 - self._button_width * scale, v-50),
            size=(self._button_width, self._button_height),
            scale=scale,
            autoselect=self._use_autoselect,
            label=bs.Lstr(resource=self._r + '.settingsText'),
            transition_delay=self._tdelay,
            on_activate_call=self._settings)
        self._server_button3 = bui.buttonwidget(
            parent=self._root_widget,
            position=(h * 3.2 + 20 - self._button_width * scale, v-100),
            size=(self._button_width, self._button_height),
            scale=scale,
            autoselect=self._use_autoselect,
            label=bs.Lstr(resource=self._r + '.settingsText'),
            transition_delay=self._tdelay,
            on_activate_call=self._settings)

    else:
        h, v, scale = self._refresh_not_in_game(positions)

    if self._have_settings_button:
        h, v, scale = positions[self._p_index]
        self._p_index += 1
        self._settings_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(h - self._button_width * 0.5 * scale, v),
            size=(self._button_width, self._button_height),
            scale=scale,
            autoselect=self._use_autoselect,
            label=bs.Lstr(resource=self._r + '.settingsText'),
            transition_delay=self._tdelay,
            on_activate_call=self._settings)

    # Scattered eggs on easter.
    if _baplus.get_v1_account_misc_read_val('easter',
                                            False) and not self._in_game:
        icon_size = 34
        bui.imagewidget(parent=self._root_widget,
                        position=(h - icon_size * 0.5 - 15,
                                  v + self._button_height * scale -
                                  icon_size * 0.24 + 1.5),
                        transition_delay=self._tdelay,
                        size=(icon_size, icon_size),
                        texture=bui.gettexture('egg3'),
                        tilt_scale=0.0)

    self._tdelay += self._t_delay_inc

    if self._in_game:
        h, v, scale = positions[self._p_index]
        self._p_index += 1

        # If we're in a replay, we have a 'Leave Replay' button.
        if _bs.is_in_replay():
            bui.buttonwidget(parent=self._root_widget,
                             position=(h - self._button_width * 0.5 * scale,
                                       v),
                             scale=scale,
                             size=(self._button_width, self._button_height),
                             autoselect=self._use_autoselect,
                             label=bs.Lstr(resource='replayEndText'),
                             on_activate_call=self._confirm_end_replay)
        elif _bs.get_foreground_host_session() is not None:
            bui.buttonwidget(
                parent=self._root_widget,
                position=(h - self._button_width * 0.5 * scale, v),
                scale=scale,
                size=(self._button_width, self._button_height),
                autoselect=self._use_autoselect,
                label=bs.Lstr(resource=self._r + '.endGameText'),
                on_activate_call=self._confirm_end_game)
        # Assume we're in a client-session.
        else:
            bui.buttonwidget(
                parent=self._root_widget,
                position=(h - self._button_width * 0.5 * scale, v),
                scale=scale,
                size=(self._button_width, self._button_height),
                autoselect=self._use_autoselect,
                label=bs.Lstr(resource=self._r + '.leavePartyText'),
                on_activate_call=self._confirm_leave_party)

    self._store_button: Optional[bui.Widget]
    if self._have_store_button:
        this_b_width = self._button_width
        h, v, scale = positions[self._p_index]
        self._p_index += 1

        sbtn = self._store_button_instance = StoreButton(
            parent=self._root_widget,
            position=(h - this_b_width * 0.5 * scale, v),
            size=(this_b_width, self._button_height),
            scale=scale,
            on_activate_call=bs.WeakCall(self._on_store_pressed),
            sale_scale=1.3,
            transition_delay=self._tdelay)
        self._store_button = store_button = sbtn.get_button()
        uiscale = bui.app.ui_v1.uiscale
        icon_size = (55 if uiscale is bui.UIScale.SMALL else
                     55 if uiscale is bui.UIScale.MEDIUM else 70)
        bui.imagewidget(
            parent=self._root_widget,
            position=(h - icon_size * 0.5,
                      v + self._button_height * scale - icon_size * 0.23),
            transition_delay=self._tdelay,
            size=(icon_size, icon_size),
            texture=bui.gettexture(self._store_char_tex),
            tilt_scale=0.0,
            draw_controller=store_button)

        self._tdelay += self._t_delay_inc
    else:
        self._store_button = None

    self._quit_button: Optional[bui.Widget]
    if not self._in_game and self._have_quit_button:
        h, v, scale = positions[self._p_index]
        self._p_index += 1
        self._quit_button = quit_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=self._use_autoselect,
            position=(h - self._button_width * 0.5 * scale, v),
            size=(self._button_width, self._button_height),
            scale=scale,
            label=bs.Lstr(resource=self._r +
                          ('.quitText' if 'Mac' in
                           bs.app.classic.legacy_user_agent_string else '.exitGameText')),
            on_activate_call=self._quit,
            transition_delay=self._tdelay)

        # Scattered eggs on easter.
        if _baplus.get_v1_account_misc_read_val('easter', False):
            icon_size = 30
            bui.imagewidget(parent=self._root_widget,
                            position=(h - icon_size * 0.5 + 25,
                                      v + self._button_height * scale -
                                      icon_size * 0.24 + 1.5),
                            transition_delay=self._tdelay,
                            size=(icon_size, icon_size),
                            texture=bui.gettexture('egg1'),
                            tilt_scale=0.0)

        bui.containerwidget(edit=self._root_widget,
                            cancel_button=quit_button)
        self._tdelay += self._t_delay_inc
    else:
        self._quit_button = None

        # If we're not in-game, have no quit button, and this is android,
        # we want back presses to quit our activity.
        if (not self._in_game and not self._have_quit_button
                and bs.app.classic.platform == 'android'):

            def _do_quit() -> None:
                QuitWindow(swish=True, back=True)

            bui.containerwidget(edit=self._root_widget,
                                on_cancel_call=_do_quit)

    # Add speed-up/slow-down buttons for replays.
    # (ideally this should be part of a fading-out playback bar like most
    # media players but this works for now).
    if _bs.is_in_replay():
        b_size = 50.0
        b_buffer = 10.0
        t_scale = 0.75
        uiscale = bui.app.ui_v1.uiscale
        if uiscale is bui.UIScale.SMALL:
            b_size *= 0.6
            b_buffer *= 1.0
            v_offs = -40
            t_scale = 0.5
        elif uiscale is bui.UIScale.MEDIUM:
            v_offs = -70
        else:
            v_offs = -100
        self._replay_speed_text = bui.textwidget(
            parent=self._root_widget,
            text=bs.Lstr(resource='watchWindow.playbackSpeedText',
                         subs=[('${SPEED}', str(1.23))]),
            position=(h, v + v_offs + 7 * t_scale),
            h_align='center',
            v_align='center',
            size=(0, 0),
            scale=t_scale)

        # Update to current value.
        self._change_replay_speed(0)

        # Keep updating in a timer in case it gets changed elsewhere.
        self._change_replay_speed_timer = bs.Timer(
            0.25,
            bs.WeakCall(self._change_replay_speed, 0),
            repeat=True)
        btn = bui.buttonwidget(parent=self._root_widget,
                               position=(h - b_size - b_buffer,
                                         v - b_size - b_buffer + v_offs),
                               button_type='square',
                               size=(b_size, b_size),
                               label='',
                               autoselect=True,
                               on_activate_call=bs.Call(
                                   self._change_replay_speed, -1))
        bui.textwidget(
            parent=self._root_widget,
            draw_controller=btn,
            text='-',
            position=(h - b_size * 0.5 - b_buffer,
                      v - b_size * 0.5 - b_buffer + 5 * t_scale + v_offs),
            h_align='center',
            v_align='center',
            size=(0, 0),
            scale=3.0 * t_scale)
        btn = bui.buttonwidget(
            parent=self._root_widget,
            position=(h + b_buffer, v - b_size - b_buffer + v_offs),
            button_type='square',
            size=(b_size, b_size),
            label='',
            autoselect=True,
            on_activate_call=bs.Call(self._change_replay_speed, 1))
        bui.textwidget(
            parent=self._root_widget,
            draw_controller=btn,
            text='+',
            position=(h + b_size * 0.5 + b_buffer,
                      v - b_size * 0.5 - b_buffer + 5 * t_scale + v_offs),
            h_align='center',
            v_align='center',
            size=(0, 0),
            scale=3.0 * t_scale)


# ba_meta export plugin
class bySmoothy(babase.Plugin):
    def __init__(self):
        if babase.env().get("build_number", 0) >= 21140:
            bastd_ui_mainmenu.MainMenuWindow._refresh_in_game = new_refresh_in_game
            bs.connect_to_party = newconnect_to_party
            bs.disconnect_from_host = newdisconnect_from_host
        else:
            print("Server Switch  only works on bs 1.7.20 and above")
