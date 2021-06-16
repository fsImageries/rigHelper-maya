_HELP = {
    "selectGrp":
    """
Select the group tranform of the skeleton, from this it's going to find all other joints and tries to center
the transform based on the first joint coming after.
""",
    "centerGrp":
    """
Center the transform by positioning the pivot at the top most joints position and moving it back to scenes nullpoint.
""",
    "zeroZ":
    """
Zero out Z value of all joints accept the ones which got supplied. Skipables defaults to [hip, legs_joints].
""",
    "zeroLegs":
    """
Zero the Y value of the top leg joints and the X value of all subsequent children.
""",
    "zeroSpines":
    """
Zero the X value of the spine joints.
""",
    "poseArms":
    """
Try to pose the arm joints by drawing a curve in 45 degree and snaping the arm joints to the nearest position on the curve.
""",
    "mirrorJoints":
    """
Mirror a joint chain around the X position, chains need to have the same amount of children.
""",
    "keyAll":
    """
Key all children basend on the internal group thats selected.
""",
    "unkeyAll":
    """
Delete all keys based on the selected attribute.
""",
    "restJoints":
    """
Scale the joints, in it's pointing direction, by the longest distance the rig will reach.
It goes over keys applied on the joints and keeps track of the furthes distance they reach,
after that it will move the joints to reach that distance. 
Used to apply correct Ik-Handles which don't understretch.
""",
    "dupSpecial":
    """
Simple duplicateSpecial wrapper, you only have to select the top most tranform. It will duplicate everything
downstream.
You can supply a src and target name for the original and duplicated object.
Used for Ik-transfer tools to create a src and target group for constraining.
""",
    "ikRPS":
    """
Creates a simple Ik-Handle (RotatePlaneSolver) used for appendices, eg. arms and legs, which gets contrained to the given src transforms.
The src_jnt drives the resulting ik handle and should be positioned at resulting end of the ik chain.
The polevec_jnt drives the pole vector of the ik chain and should be positioned accordingly. 
They're named joints but can be everything that is a transform.
""",
    "ikS":
    """
Create a spline Ik-Handle with the Ik-SplineHandleTool from the supplied spine joints.
It will create 2 cluster paired to the cvs of the driving crv, these clusters will get contrained 
to the given src_jnts. One for the upper cluster and one for the lower.
""",
"ikConstraint":
"""
Simple GUI wrapper for constraining objects by the given nodes.
""",
    "importBtn":
    """
Import a VideoPose3D skeleton given as .Json.
You can deley the incoming animation by the given amount in frames.
""",
    "locTrans":
    """
Creates a locator which will be paired to the incoming connections of the joint.
The locator will get zerod on the joint position and its position add to the incoming values.
It's used to transform already animated joints without working around keyframes.
Use the remove button to establish the original connections.
""",
    "unchangingKeys":
    """
Find unchanging keyframes on the selected objects.
This function works in 2 modes,
    1. Unchanging Keyframes
    This will display animation curves which have Keyframes which values don't change over time.

    2. Unchanging Key-Ranges
    This will display periods of time in which the values of animation curves don't change.
    It will look if there are more than 2 values in a range to determine if it should show the range.

The 'Recurse' checkbox determines if children of the node should also be looked at.
"""

}
