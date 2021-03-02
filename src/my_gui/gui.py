import Tkinter
import tkMessageBox
import rospy
from popups import NewHomePosition

from geometry_msgs.msg import InertiaStamped, Vector3, PoseStamped
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus

from indoors_common.srv import Cmd


class HomePosition:
    def __init__(self, new_position):
        self._position = new_position


class my_gui:
    """
    docstring
    """

    def __init__(self):
        rospy.init_node('my_gui', anonymous=True)
        self.top = Tkinter.Tk()
        self.grid = Tkinter.Grid()
        # Simple text
        self.T = Tkinter.Text(self.top, height=2, width=30)
        self.Tmode = Tkinter.Text(self.top, height=2, width=30)
        self.Tsite = Tkinter.Text(self.top, height=2, width=30)
        self.buttons = {}

        # Movements buttons
        self.manual_delta_size = 1
        self.manual_delta_rotattion_step = 45
        self._is_movements_buttons_disabled = False

        # Arm and takeoff
        self.buttons['ArmAndTakeoffBtn'] = Tkinter.Button(
            self.top, text="ArmAndTakeoff", command=self.armAndTakeoffGuiCallBack)
        # Arm
        self.buttons['ArmBtn'] = Tkinter.Button(
            self.top, text="Arm", command=self.armGuiCallBack)

        # Disarm
        self.buttons['DisarmBtn'] = Tkinter.Button(
            self.top, text="Disarm", command=self.disarmGuiCallBack)

        # Takeoff
        self.buttons['TakeoffBtn'] = Tkinter.Button(
            self.top, text="Takeoff", command=self.takeoffGuiCallBack)

        # Land
        self.buttons['LandBtn'] = Tkinter.Button(
            self.top, text="Land", command=self.landGuiCallBack)

        # Exploration
        self.buttons['ExplorationBtn'] = Tkinter.Button(
            self.top, text="ExplorationStart", command=self.explorationStartGuiCallBack)

        # HoldPosition
        self.buttons['HoldPositionBtn'] = Tkinter.Button(
            self.top, text="HoldPosition", command=self.holdPositionGuiCallBack)

        # ManualEnable
        self.buttons['ManualEnableBtn'] = Tkinter.Button(
            self.top, text="ManualEnable", command=self.manualEnableGuiCallBack)

        # ManualMovements
        self.movements_btns = [
            Tkinter.Button(self.top, text="Left",
                           command=self.deltaLeftGuiCallBack),
            Tkinter.Button(self.top, text="Forward",
                           command=self.deltaForwardGuiCallBack),
            Tkinter.Button(self.top, text="Backward",
                           command=self.deltaBackwarddGuiCallBack),
            Tkinter.Button(self.top, text="Right",
                           command=self.deltaRightGuiCallBack),
            Tkinter.Button(self.top, text="Up",
                           command=self.deltaUpGuiCallBack),
            Tkinter.Button(self.top, text="Down",
                           command=self.deltaDownGuiCallBack),
            Tkinter.Button(self.top, text="RotateCCW",
                           command=self.deltaRotateCCWGuiCallBack),
            Tkinter.Button(self.top, text="RotateCW",
                           command=self.deltaRotateCWGuiCallBack),
        ]
        # ManualDisable
        self.buttons['ManualDisableBtn'] = Tkinter.Button(
            self.top, text="ManualDisable", command=self.manualDisableGuiCallBack)

        # Indoors
        self.buttons['IndoorsBtn'] = Tkinter.Button(
            self.top, text="Indoors", command=self.indoorsGuiCallBack)

        # Outdoors
        self.buttons['OutdoorsBtn'] = Tkinter.Button(
            self.top, text="Outdoors", command=self.outdoorsGuiCallBack)

        # GoHome
        self.buttons['GoHomeBtn'] = Tkinter.Button(
            self.top, text="GoHome", command=self.goHomeGuiCallBack)

        # Set NewHomePosition
        self.buttons['NewHomePositionBtn'] = Tkinter.Button(
            self.top, text="NewHomePosition", command=self.newHomePositionGuiCallBack)

        self.stop_manual_only_publisher = rospy.Publisher(
            '/sm/wp/command', InertiaStamped, queue_size=1)

        self.commands_publisher = rospy.Publisher(
            '/communication_manager/out/command', InertiaStamped, queue_size=1)

        self.go_to_node_publisher = rospy.Publisher(
            '/communication_manager/out/move_base_simple/goal', PoseStamped, queue_size=1)

        self.set_new_home_position_publisher = rospy.Publisher(
            '/path_planner/in/new_home_position', PoseStamped, queue_size=1)

        self.bit_ffk_node_subscriber = rospy.Subscriber(
            '/bit/FFK_node', DiagnosticArray, self.ffkRosCallBack)

        self.path_planner_out_home_position_subscriber = rospy.Subscriber(
            '/path_planner/out/home_position', PoseStamped, self.pathPlannerHomePositionRosCallBack)

        self.init_services()
        self.tick = None
        self.site_status = None
        self.system_status = None

    def init_services(self):
        """
        rosservice call /FFK_node/set_command "command: 'CMD_CHANGE_SITE_TO_INDOOR'"
        """
        rospy.wait_for_service('/FFK_node/set_command')
        self.ffk_set_command_service = rospy.ServiceProxy(
            '/FFK_node/set_command', Cmd)

    def resetcolors(self):
        for botton in self.buttons.values():
            botton.configure(bg="gray")

    def start(self):
        column = 1

        self.Tsite.grid(column=column, row=0)
        self.Tmode.grid(column=column+1, row=0)

        self.buttons['DisarmBtn'].grid(column=column, row=2)
        self.buttons['ArmBtn'].grid(column=column, row=3)
        self.buttons['ArmAndTakeoffBtn'].grid(column=column + 1, row=3)
        self.buttons['TakeoffBtn'].grid(column=column, row=4)
        self.buttons['LandBtn'].grid(column=column, row=5)
        self.buttons['HoldPositionBtn'].grid(column=column, row=6)
        self.buttons['GoHomeBtn'].grid(column=column+1, row=6)
        self.buttons['NewHomePositionBtn'].grid(column=column+2, row=6)
        self.buttons['ExplorationBtn'].grid(column=column, row=7)
        self.buttons['ManualEnableBtn'].grid(column=column, row=8)
        self.buttons['ManualEnableBtn'].configure(state=Tkinter.DISABLED)

        # # grid = Tkinter.Grid(self.top)
        self.init_movement_buttons()

        self.buttons['ManualDisableBtn'].grid(column=column, row=10)
        self.buttons['ManualDisableBtn'].configure(state=Tkinter.DISABLED)
        self.buttons['IndoorsBtn'].grid(column=column, row=11)
        self.buttons['OutdoorsBtn'].grid(column=column, row=12)
        self.T.grid(column=column, row=13)
        self.top.mainloop()

    def init_movement_buttons(self):
        for button_num in range(0, len(self.movements_btns)):
            self.movements_btns[button_num].grid(column=button_num, row=9)

        # self.disable_movements_buttons()

    def disable_movements_buttons(self):
        for button_num in range(0, len(self.movements_btns)):
            self.movements_btns[button_num].config(state=Tkinter.DISABLED)
        self._is_movements_buttons_disabled = True

    def enable_movements_buttons(self):
        for button_num in range(0, len(self.movements_btns)):
            self.movements_btns[button_num].config(state=Tkinter.NORMAL)
        self._is_movements_buttons_disabled = False

    def ffkRosCallBack(self, data):
        tock = rospy.Time.now()
        if self.tick is None:
            self.tick = tock

        # Indoor \ Outdoor timing
        if self.site_status != data.status[0].values[1].value:
            self.site_status = data.status[0].values[1].value
            if self.site_status == "OUTDOOR":
                self.Tsite.insert(Tkinter.END, self.site_status +
                                  ": "+str((tock - self.tick).to_sec()) + "[ms]\n")
                self.Tsite.see("end")

                self.buttons['OutdoorsBtn'].configure(bg="green")
                self.buttons['IndoorsBtn'].configure(bg="gray")

            if self.site_status == "INDOOR":
                self.Tsite.insert(Tkinter.END, self.site_status +
                                  ": "+str((tock - self.tick).to_sec()) + "[ms]\n")
                self.Tsite.see("end")

                self.buttons['OutdoorsBtn'].configure(bg="gray")
                self.buttons['IndoorsBtn'].configure(bg="green")

        # State transitioning timing
        if self.system_status != data.status[0].values[0].value:
            self.system_status = data.status[0].values[0].value

            if self.system_status == "DISARMED":
                self.T.insert(
                    Tkinter.END, "Roundtrip time [ms]: "+str((tock - self.tick).to_sec()) + "\n")

                self.resetcolors()
                self.buttons['DisarmBtn'].configure(bg="green")

            if self.system_status == "ON_GROUND":
                self.T.insert(
                    Tkinter.END, "Roundtrip time [ms]: "+str((tock - self.tick).to_sec()) + "\n")

                self.resetcolors()
                self.buttons['ArmBtn'].configure(bg="red")

            if self.system_status == "EXPLORATION":
                self.T.insert(
                    Tkinter.END, "Roundtrip time [ms]: "+str((tock - self.tick).to_sec()) + "\n")

                self.resetcolors()
                self.buttons['ExplorationBtn'].configure(bg="green")

            if self.system_status == "HOLDING_POSITION":
                self.T.insert(
                    Tkinter.END, "Roundtrip time [ms]: "+str((tock - self.tick).to_sec()) + "\n")

                self.resetcolors()
                self.buttons['HoldPositionBtn'].configure(bg="green")

            if self.system_status == "MANUAL":
                self.T.insert(
                    Tkinter.END, "Roundtrip time [ms]: "+str((tock - self.tick).to_sec()) + "\n")

                self.resetcolors()
                self.buttons['ManualEnableBtn'].configure(bg="green")
            #     if self._is_movements_buttons_disabled is True:
            #         self.enable_movements_buttons()

            # if self.system_status != "MANUAL" and self._is_movements_buttons_disabled is False:
            #     self.disable_movements_buttons()

            self.T.see("end")

        self.Tmode.insert(Tkinter.END, self.system_status + "\n")
        self.Tmode.see("end")

    def pathPlannerHomePositionRosCallBack(self, data):
        self._home_position = HomePosition(data)

    def armAndTakeoffGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 20
        msg.inertia.com = Vector3(x=0, y=0, z=1)
        self.commands_publisher.publish(msg)

    def armGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 1
        self.commands_publisher.publish(msg)

    def disarmGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 0
        self.commands_publisher.publish(msg)

    def takeoffGuiCallBack(self):
        # Dont time this command
        msg = InertiaStamped()
        msg.inertia.m = 2
        msg.inertia.com = Vector3(x=0, y=0, z=1)
        self.commands_publisher.publish(msg)

    def landGuiCallBack(self):
        # Dont time this command
        msg = InertiaStamped()
        msg.inertia.m = 3
        self.commands_publisher.publish(msg)

    def explorationStartGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 11
        self.commands_publisher.publish(msg)

    def holdPositionGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 5
        self.commands_publisher.publish(msg)

    def manualEnableGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.com = Vector3(x=0, y=0, z=1)
        self.commands_publisher.publish(msg)

    def deltaLeftGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.com = Vector3(x=0, y=self.manual_delta_size, z=0)
        self.commands_publisher.publish(msg)

    def deltaRotateCCWGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.ixz = self.manual_delta_rotattion_step
        self.commands_publisher.publish(msg)

    def deltaRotateCWGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.ixz = - self.manual_delta_rotattion_step
        self.commands_publisher.publish(msg)

    def deltaRightGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.com = Vector3(x=0, y=- self.manual_delta_size, z=0)
        self.commands_publisher.publish(msg)

    def deltaForwardGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.com = Vector3(x=self.manual_delta_size, y=0, z=0)
        self.commands_publisher.publish(msg)

    def deltaBackwarddGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.com = Vector3(x=- self.manual_delta_size, y=0, z=0)
        self.commands_publisher.publish(msg)

    def deltaUpGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.com = Vector3(x=0, y=0, z=self.manual_delta_size)
        self.commands_publisher.publish(msg)

    def deltaDownGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 7
        msg.inertia.com = Vector3(x=0, y=0, z=- self.manual_delta_size)
        self.commands_publisher.publish(msg)

    def manualDisableGuiCallBack(self):
        self.tick = rospy.Time.now()
        msg = InertiaStamped()
        msg.inertia.m = 10
        msg.inertia.com = Vector3(x=0, y=0, z=1)
        self.stop_manual_only_publisher.publish(msg)

    def indoorsGuiCallBack(self):
        self.tick = rospy.Time.now()
        respond = self.ffk_set_command_service("CMD_CHANGE_SITE_TO_INDOOR")

        # msg = InertiaStamped()
        # msg.inertia.m = 10
        # msg.inertia.com = Vector3(x=0, y=0, z=1)
        # self.stop_manual_only_publisher.publish(msg)

    def outdoorsGuiCallBack(self):
        self.tick = rospy.Time.now()
        respond = self.ffk_set_command_service("CMD_CHANGE_SITE_TO_OUTDOOR")

    def goHomeGuiCallBack(self):
        self.go_to_node_publisher.publish(self._home_position._position)

    def newHomePositionGuiCallBack(self):
        self.new_home_window = NewHomePosition(self.top)
        self.buttons['NewHomePositionBtn']["state"] = "disabled"
        self.top.wait_window(self.new_home_window.top)

        set_new_home = PoseStamped()
        set_new_home.pose.position.x = self.new_home_window.home_position_xyz[0]
        set_new_home.pose.position.y = self.new_home_window.home_position_xyz[1]
        set_new_home.pose.position.z = self.new_home_window.home_position_xyz[2]
        set_new_home.pose.orientation.x = self.new_home_window.home_orientation_xyzw[0]
        set_new_home.pose.orientation.y = self.new_home_window.home_orientation_xyzw[1]
        set_new_home.pose.orientation.z = self.new_home_window.home_orientation_xyzw[2]
        set_new_home.pose.orientation.w = self.new_home_window.home_orientation_xyzw[3]
        self.set_new_home_position_publisher.publish(set_new_home)
        
        rospy.loginfo("Got new home. setting new home in path planner")
        rospy.loginfo(set_new_home)

        self.buttons['NewHomePositionBtn']["state"] = "normal"
