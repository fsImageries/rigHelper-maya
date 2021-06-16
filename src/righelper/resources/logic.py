import maya.cmds as cmds
import sys

path = "/Users/joshua/Desktop/mayapyUtils/src"
if path not in sys.path:
    sys.path.append(path)

from mayapyUtils.righelper import *
from mayapyUtils import pyhelper


class RigHelper_logic(object):

    @staticmethod
    def import_videopose_skel(filepath, delay=None):
        pose = import_videopose(filepath)
        if delay:
            move_keyframes(pose.group, mv=delay)

        return pose.group

    @staticmethod
    def get_selection(child=False, rec=False):
        sel = cmds.ls(sl=True, l=True)

        if not sel: 
            return None

        if child:
            childs = [cmds.listRelatives(s, shapes=not rec, ad=rec, f=True) for s in sel]
            return sel + pyhelper.flatten(childs)
        return sel
    
    def sel_group(self, group=None):
        if group:
            self.group = group
        else:
            try:
                self.group = cmds.ls(sl=True, l=True)[0]
            except IndexError:
                raise IndexError("Nothing Selected.")

        self.all_jnts = cmds.listRelatives(self.group, ad=True, f=True)

    def automate_pose(self):
        self.center_group()
        self.zero_all()
        self.zero_legs()
        self.zero_spines()
        self.pose_arms()
        self.key_all(tr=True)

        print("Finished posing, check the arm and leg chains for errors.\nMaybe mirror and rest some chains.")

    def automate_ik(self):
        _, tar_grp = self.duplicate_special(["skel_src", "skel_tar"])

        l_arms = [12,14,14,13]
        r_arms = [15,17,17,16]

        l_legs = [5,7,7,6]
        r_legs = [2,4,4,3]

        spines = [1,9,9,8]

        ik_chains = [l_arms, r_arms, l_legs,r_legs,spines]
        target_jnts = cmds.listRelatives(tar_grp, ad=True, f=True)

        for n,idx in enumerate(ik_chains):
            src_ids = idx[:2]
            tar_ids = idx[2:]
            src_jnts = joint_search(target_jnts, src_ids)
            tar_jnts = joint_search(self.all_jnts, tar_ids)
            
            if n == len(ik_chains)-1:
                self.ik_spline_transfer(src_jnts+tar_jnts)
            else:
                self.ik_transfer(src_jnts+tar_jnts)

        self.unkey_all(jnts=target_jnts, skips=joint_search(target_jnts, [1]), tr=True)

        # toConst = [15,12]
        # for const in toConst:
        #     src = joint_search(self.all_jnts, [const])
        #     tar = joint_search(target_jnts, [const])

        #     self.constraining(src+tar, "parentConstraint", mo=True)

    # Posing
    def center_group(self):
        center_chain_transform(
            self.group, cmds.listRelatives(self.group, c=True, f=True)[0])

    def zero_all(self, skips=None):
        if not skips:
            skips = [10, 11, 4, 7]

        if not isinstance(skips[0], basestring):
            length = len(self.all_jnts) + 1
            jnts = joint_search(
                self.all_jnts, [i for i in range(length) if not i in skips])
        else:
            jnts = skips

        all_jnts_pose(jnts)

    def zero_legs(self, ids=None):
        if not ids:
            ids = [5, 2]

        if not isinstance(ids[0], basestring):
            leg_jnts = joint_search(self.all_jnts, ids)
        else:
            leg_jnts = ids

        leg_jnts_pose(leg_jnts)

    def zero_spines(self, ids=None):
        if not ids:
            ids = [8, 9]

        if not isinstance(ids[0], basestring):
            spine_jnts = joint_search(self.all_jnts, ids)
        else:
            spine_jnts = ids

        spine_jnts_pose(spine_jnts)

    def pose_arms(self, ids=None):
        if not ids:
            ids = [15, 12]

        if not isinstance(ids[0], basestring):
            arm_jnts = joint_search(self.all_jnts, ids)
        else:
            arm_jnts = ids
        arm_jnts_pose(arm_jnts, clean=True)

    def mirror_joints(self, ids):
        if not isinstance(ids[0], basestring):
            first, second = joint_search(self.all_jnts, ids)
        else:
            first, second = ids

        mirror_jnts(first, second)

    def rest_joints(self, ids):
        t_range = max(max(cmds.keyframe(jnt, q=True, tc=True))
                      for jnt in self.all_jnts)
        for pair in ids:
            if not isinstance(pair[0], basestring):
                first, second = joint_search(self.all_jnts, pair)
            else:
                first, second = pair

            rest_length(first, second, t_range)

    def key_all(self, tr=None, ro=None):
        for jnt in self.all_jnts:
            if tr:
                cmds.setKeyframe(jnt, at="translate")
            if ro:
                cmds.setKeyframe(jnt, at="rotate")

    def unkey_all(self,skips=None, tr=None, ro=None, jnts=None):
        jnts = self.all_jnts if not jnts else jnts
        for jnt in jnts:
            if jnt in skips: continue
            if tr:
                cmds.cutKey(jnt, at="translate")
            if ro:
                cmds.cutKey(jnt, at="rotate")

    # Ik-ing
    def duplicate_special(self, ids):
        src, dup = make_src_tar(*[self.group]+ids)
        self.sel_group(src)
        # self.group = src
        return src, dup

    def ik_transfer(self, ids):
        ik_transfer(*ids)

    def ik_spline_transfer(self, ids):
        ikSpline_transfer(*ids)

    def constraining(self, ids, constraint, mo=False):
        func = getattr(cmds, constraint)
        src, dst = ids
        return func(src, dst, mo=mo)

    # Misc
    def create_locTrans(self):
        try:
            jnt = cmds.ls(sl=True)[0]
        except IndexError:
            raise ValueError("Nothing selected.")

        loc_transformer(jnt)

    def remove_locTrans(self):
        try:
            loc = cmds.ls(sl=True)[0]
        except IndexError:
            raise ValueError("Nothing selected.")
            
        remove_loc_transformer(loc)

    # Keyframes
    def sel_unchanging_keys(self, rec=False):
        sel = self.get_selection(child=True, rec=rec)
        if not sel:
            print("Nothing Selected.")
            return []

        return unchanging_animCurves(sel)

    def sel_unchanging_ranges(self, rec=False):
        sel = self.get_selection(child=True, rec=rec)
        if not sel:
            print("Nothing Selected.")
            return []

        return unchanging_ranges(sel)

    def remove_unchKeys(self, data, ranges=False):
        if ranges:
            [[cmds.cutKey(nd, time=r, clear=True) for r in ranges] for nd, ranges in data]
        else:
            for nd, _ in data: cmds.delete(nd)
    