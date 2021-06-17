from PySide2 import QtWidgets, QtCore, QtGui

from mayapyUtils import mahelper
from resources import logic, help_str, classes
from resources.ui import ui_raw


SHELF_NAME = "Custom"
SHELF_TOOL = {
    "label": "rigHelper",
    "command": "from righelper.righelper import RigHelper_ui\nRigHelper_ui.display()",
    "annotation": "Convenient Gui for general riging functions.",
    "image1": "pythonFamily.png",
    "sourceType": "python",
    "imageOverlayLabel": "rigHelper"
}


def shelf():
    mahelper._set_shelfBTN(SHELF_TOOL, SHELF_NAME)


class RigHelper_ui(QtWidgets.QMainWindow, ui_raw.Ui_RigHelper):

    UI_NAME = "RigHelper"
    WINDOW_TITLE = "Rig Helper"
    UI_INSTANCE = None

    # -------------------------------- GUI Call --------------------------- #
    # --------------------------------------------------------------------- #

    @classmethod
    def display(cls):
        """
        Is used when in production.
        Manages a RigHelper_ui instance and restores it when hiden or closed.
        """
        if cls.UI_INSTANCE:
            cls.UI_INSTANCE.workspaceControl_instance.show_workspaceControl(
                cls.UI_INSTANCE)
        else:
            cls.UI_INSTANCE = cls(mahelper.getMayaWin())

    @classmethod
    def get_uiScript(cls):
        """
        Get script with which the ShaderHelper_app is shown to restore it on start-up.

        Returns:
            [String]: Display method from ShaderHelper_app.
        """
        module_name = cls.__module__
        if module_name == "__main__":
            # -used in interactive session for testing
            module_name = cls.module_name_override

        uiScript = "from {0} import {1}\n{1}.display()".format(
            module_name, cls.__name__)
        return uiScript

    # -------------------------------- GUI Setup -------------------------- #
    # --------------------------------------------------------------------- #

    def __init__(self, parent=None):
        """
        Register a Color Managment Config Changed callback to refresh the colorspaces accordingly.

        Instantiate the ShaderHelper as logic variable.

        Setup the ShaderHelper Ui and call the WorkspaceControl after it to parent the full Ui.
        """
        super(RigHelper_ui, self).__init__(parent)

        self.setupUi(self)

        self.logic = logic.RigHelper_logic()
        self.setupControlls()
        self.setupConnections()

        mahelper.WorkspaceControl.create_workspaceControl(self)

    def setupControlls(self):
        self.unchangingKeys_view.verticalHeader().setVisible(False)

        self.cur_grp = QtWidgets.QLabel()
        self.cur_grp_str = "Current Group: {}"
        self.cur_grp.setText(self.cur_grp_str.format("None"))
        self.statusbar.addWidget(self.cur_grp)

        self.helpicon = QtGui.QIcon(":/help.png")
        self.selecticon = QtGui.QIcon(":/aselect.png")

        self._grey_out_posing()

        # Setup Help Buttons
        btns = (d for d in dir(self) if "_help" in d and not d.startswith("_"))
        for btn in btns:
            self._set_icon(getattr(self, btn), "help")

        # Setup Selection Buttons
        btns = (d for d in dir(self) if "_sel" in d and not d.startswith("_"))
        for btn in btns:
            self._set_icon(getattr(self, btn), "select")

        # Videopose tab
        self.check_delay()

        # T-Posing tab

    def setupConnections(self):
        # Videopose
        self.delayAnim.stateChanged.connect(self.delayAnim_toggle)
        self.importBtn.pressed.connect(self.importBtn_pressed)

        self.poseAutomate.pressed.connect(self.logic.automate_pose)
        self.ikAutomate.pressed.connect(self.logic.automate_ik)

        # T-Posing
        self.selectGrp.pressed.connect(self._update_cur_grp)
        self.centerGrp.pressed.connect(self.centerGrp_pressed)

        self.zeroZ.pressed.connect(self.zeroZ_pressed)
        self.zeroLegs.pressed.connect(self.zeroLegs_pressed)
        self.zeroSpines.pressed.connect(self.zeroSpines_pressed)
        self.poseArms.pressed.connect(self.poseArms_pressed)
        self.mirrorJoints.pressed.connect(self.mirrorJoints_pressed)
        self.keyAll.pressed.connect(self.keyAll_pressed)
        self.unkeyAll.pressed.connect(lambda: self.keyAll_pressed(remove=True))
        self.restJoints.pressed.connect(self.restJoints_pressed)

        # Ik-ing
        self.dupSpecial.pressed.connect(self.dupSpecial_pressed)
        self.ikRPS.pressed.connect(self.ikRPS_pressed)
        self.ikS.pressed.connect(self.ikS_pressed)

        self.ikConstraint.pressed.connect(self.ikConstraint_pressed)

        # Misc
        self.locTrans.pressed.connect(self.locTrans_pressed)
        self.locTrans2.pressed.connect(self.locTrans2_pressed)

        # Keyframes
        self.unchangingKeys.pressed.connect(self.unchangingKeys_pressed)
        self.unchangingKeyranges.pressed.connect(
            lambda: self.unchangingKeys_pressed(True))

        self.removeAll_unchKeys.pressed.connect(self.remove_unchKeys_pressed)
        self.removeSel_unchKeys.pressed.connect(
            lambda: self.remove_unchKeys_pressed(sel=True))

        # Connect Selection buttons with associated lineEdits
        btns = [d for d in dir(self) if "_sel" in d and not d.startswith("_")]
        for btn in btns:
            widget = getattr(self, btn)
            lineedit = getattr(self, btn.replace("_sel", "_sources"))
            widget.pressed.connect(lambda x=lineedit: self.select_sources(x))

        # Connect Help buttons with associated messages
        btns = [d for d in dir(self) if "_help" in d and not d.startswith("_")]
        for btn in btns:
            name = btn.replace("_help", "")
            msg = help_str._HELP.get(name, None)
            if msg:
                widget = getattr(self, btn)
                widget.pressed.connect(lambda x=msg: self.print_out(x))

    # ------------------------------- GUI Helpers ------------------------- #
    # --------------------------------------------------------------------- #

    # General
    def _set_icon(self, obj, mode):
        icon = getattr(self, "{0}icon".format(mode))

        obj.setFixedSize(24, 24)
        obj.setIcon(icon)
        obj.setIconSize(QtCore.QSize(16, 16))

    def _check_sources(self, sources):
        ids = sources.text()

        if ids:
            try:
                ids = [int(s) for s in ids.split(",")]
            except ValueError as err:
                ids = [s.strip() for s in ids.split(",")]
        return ids

    def _update_cur_grp(self, group=None):
        self.logic.sel_group(group)
        self.cur_grp.setText(self.cur_grp_str.format(self.logic.group))
        self.selectGrp_out.setText(self.logic.group)
        self._grey_out_posing()

    def _get_d(self, i):
        return self.unchangingKeys_view.model().data(i, QtCore.Qt.DisplayRole)

    def _get_0(self, i):
        return self.unchangingKeys_view.model().index(i.row(), 0)

    def _get_selected_ranges(self):
        indices = self.unchangingKeys_view.selectedIndexes()

        sel = []
        for i in indices:
            # get selection
            # if 0th column isn't chosen, get it
            # get selected ranges

            if i.column() == 0:
                continue

            nd_idx = self._get_0(i)
            nd = self._get_d(nd_idx)
            rang = self._get_d(i)

            if not rang:
                continue

            rang = tuple(int(i) for i in rang[1:-1].split(", "))
            sel.append([nd, [rang]])

        return sel

    def _get_selected_anims(self):
        indices = self.unchangingKeys_view.selectedIndexes()
        tmp = {self._get_d(i) if i.column() == 0 else self._get_d(
            self._get_0(i)) for i in indices}
        return list(tmp)

    def _grey_out_posing(self):
        li = self.posing_tab.findChildren(QtWidgets.QPushButton)
        for l in li:
            name = l.objectName()
            if "_sel" in name or "_help" in name or "selectGrp" in name:
                continue
            l.setEnabled(bool(vars(self.logic).get("group", None)))

    # Videopose tab
    def check_delay(self):
        if self.delayAnim.isChecked():
            self.delayBy.setEnabled(True)
            return

        self.delayBy.setEnabled(False)

    # -------------------------------- GUI Slots -------------------------- #
    # --------------------------------------------------------------------- #

    def print_out(self, msg):
        print(msg)

    def select_sources(self, output):
        sel = self.logic.get_selection()
        if not sel:
            print("Nothing Selected.")
            return
        output.setText(", ".join(sel))

    # Videopose tab
    def delayAnim_toggle(self):
        self.check_delay()

    def importBtn_pressed(self):
        ff = "Json Files (*.json)"
        path = mahelper.get_filePath(ff=ff)

        if path:
            delay = self.delayBy.value() if self.delayAnim.isChecked() else None
            group = self.logic.import_videopose_skel(path[0], delay)

            # self.selectGrp_pressed(group)
            self._update_cur_grp(group)

    # T-Posing tab
    def selectGrp_pressed(self, group=None):
        self.logic.sel_group(group)
        self._update_cur_grp(self.logic.group)

    def centerGrp_pressed(self):
        self.logic.center_group()

    def zeroZ_pressed(self):
        skips = self._check_sources(self.zeroZ_sources)
        self.logic.zero_all(skips=skips if skips else None)

    def zeroLegs_pressed(self):
        self.logic.zero_legs()

    def zeroSpines_pressed(self):
        self.logic.zero_spines()

    def poseArms_pressed(self):
        self.logic.pose_arms()

    def mirrorJoints_pressed(self):
        ids = self._check_sources(self.mirrorJoints_sources)

        if not ids:
            raise ValueError("No input given.")

        if len(ids) != 2:
            raise ValueError("Wrong Number of inputs, 2 needed.")

        self.logic.mirror_joints(ids)

    def keyAll_pressed(self, remove=None):
        trans = True if self.keyAll_translate.isChecked() else None
        rot = True if self.keyAll_rotate.isChecked() else None

        if remove:
            self.logic.unkey_all(tr=trans, ro=rot)
        else:
            self.logic.key_all(tr=trans, ro=rot)

    def restJoints_pressed(self):
        ids = self._check_sources(self.restJoints_sources)

        if not ids:
            raise ValueError("No input given.")

        if len(ids) % 2 != 0 or len(ids) < 2:
            raise ValueError("Wrong Number of inputs, pairs of 2 needed.")

        ids = [[i, ids[n+1]] for n, i in enumerate(ids) if n % 2 == 0]

        self.logic.rest_joints(ids)

    # Ik-ing
    def dupSpecial_pressed(self):
        ids = self._check_sources(self.dupSpecial_sources)

        if not ids:
            ids = [None]*2

        if len(ids) != 2:
            raise ValueError("Wrong Number of inputs, 2 needed when given.")

        src, dup = self.logic.duplicate_special(ids)
        self._update_cur_grp(src)

    def ikRPS_pressed(self):
        ids = self._check_sources(self.ikRPS_sources)

        if not ids:
            raise ValueError("No input given.")

        if len(ids) != 4:
            raise ValueError("Wrong Number of inputs, 2 needed when given.")

        self.logic.ik_transfer(ids)

    def ikS_pressed(self):
        ids = self._check_sources(self.ikS_sources)

        if not ids:
            raise ValueError("No input given.")

        if len(ids) != 4:
            raise ValueError("Wrong Number of inputs, 2 needed when given.")

        self.logic.ik_spline_transfer(ids)

    def ikConstraint_pressed(self):
        ids = self._check_sources(self.ikConstraint_sources)

        if not ids:
            raise ValueError("No input given.")
        if len(ids) != 2:
            raise ValueError("Wrong Number of inputs, 2 needed.")

        constraint = self.ikConstraint_type.currentData(QtCore.Qt.DisplayRole)

        self.logic.constraining(ids, constraint)

    # Misc
    def locTrans_pressed(self):
        self.logic.create_locTrans()

    def locTrans2_pressed(self):
        self.logic.remove_locTrans()

    # Keyframes
    def unchangingKeys_pressed(self, ranges=False):
        rec = self.unchangingKeys_rec.isChecked()
        self.ranges = ranges

        if not ranges:
            data = self.logic.sel_unchanging_keys(rec)
            headers = "Node, Key-Value".split(", ")
            self.keyframes = data
        else:
            data = self.logic.sel_unchanging_ranges(rec)
            headers = ["Node"]
            if len(data):
                max_ranges = max([len(d) for _, d in data])
                hd_ranges = ["Key-Range{0}".format(i)
                             for i in range(max_ranges)]
                headers += hd_ranges
                self.keyframes = data
                # for display in table view
                tmp = [[nd]+[d for d in da] for nd, da in data]
                data = sorted(tmp, key=len, reverse=True)

        data = [[str(elem) for elem in da] for da in data]
        model = classes.TableModel(data, headers)

        self.unchangingKeys_model = model
        self.unchangingKeys_view.setModel(model)
        self.unchangingKeys_view.resizeColumnsToContents()

    def remove_unchKeys_pressed(self, sel=False):
        try:
            if sel:
                if self.ranges:
                    keyframes = self._get_selected_ranges()
                else:
                    keyframes = self._get_selected_anims()

                self.logic.remove_unchKeys(keyframes, self.ranges)
            else:
                self.logic.remove_unchKeys(self.keyframes, self.ranges)

            self.unchangingKeys_pressed(self.ranges)
        except AttributeError:
            print("Nothing Selected.")
            return
