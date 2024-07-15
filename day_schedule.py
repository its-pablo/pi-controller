# Form implementation generated from reading ui file '.\day_schedule.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_DaySchedule(object):
    def setupUi(self, DaySchedule):
        DaySchedule.setObjectName("DaySchedule")
        DaySchedule.resize(335, 550)
        self.verticalLayout = QtWidgets.QVBoxLayout(DaySchedule)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gb_d_sched = QtWidgets.QGroupBox(parent=DaySchedule)
        self.gb_d_sched.setObjectName("gb_d_sched")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.gb_d_sched)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tv_day_sched = QtWidgets.QTableView(parent=self.gb_d_sched)
        self.tv_day_sched.setObjectName("tv_day_sched")
        self.tv_day_sched.horizontalHeader().setCascadingSectionResizes(True)
        self.tv_day_sched.horizontalHeader().setStretchLastSection(True)
        self.tv_day_sched.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.tv_day_sched)
        self.verticalLayout.addWidget(self.gb_d_sched)
        self.gb_d_period = QtWidgets.QGroupBox(parent=DaySchedule)
        self.gb_d_period.setObjectName("gb_d_period")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.gb_d_period)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(parent=self.gb_d_period)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.hs_period = QtWidgets.QSlider(parent=self.gb_d_period)
        self.hs_period.setMinimum(0)
        self.hs_period.setMaximum(28)
        self.hs_period.setProperty("value", 0)
        self.hs_period.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.hs_period.setTickPosition(QtWidgets.QSlider.TickPosition.TicksAbove)
        self.hs_period.setTickInterval(7)
        self.hs_period.setObjectName("hs_period")
        self.horizontalLayout.addWidget(self.hs_period)
        self.label_2 = QtWidgets.QLabel(parent=self.gb_d_period)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addWidget(self.gb_d_period)
        self.gb_d_dur = QtWidgets.QGroupBox(parent=DaySchedule)
        self.gb_d_dur.setObjectName("gb_d_dur")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.gb_d_dur)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(parent=self.gb_d_dur)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.hs_dur = QtWidgets.QSlider(parent=self.gb_d_dur)
        self.hs_dur.setMinimum(1)
        self.hs_dur.setMaximum(60)
        self.hs_dur.setProperty("value", 1)
        self.hs_dur.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.hs_dur.setTickPosition(QtWidgets.QSlider.TickPosition.TicksAbove)
        self.hs_dur.setTickInterval(5)
        self.hs_dur.setObjectName("hs_dur")
        self.horizontalLayout_2.addWidget(self.hs_dur)
        self.label_4 = QtWidgets.QLabel(parent=self.gb_d_dur)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.verticalLayout.addWidget(self.gb_d_dur)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_7 = QtWidgets.QLabel(parent=DaySchedule)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.te_d_tod = QtWidgets.QTimeEdit(parent=DaySchedule)
        self.te_d_tod.setObjectName("te_d_tod")
        self.horizontalLayout_3.addWidget(self.te_d_tod)
        self.line_2 = QtWidgets.QFrame(parent=DaySchedule)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_3.addWidget(self.line_2)
        self.label_8 = QtWidgets.QLabel(parent=DaySchedule)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        self.lbl_period = QtWidgets.QLabel(parent=DaySchedule)
        self.lbl_period.setObjectName("lbl_period")
        self.horizontalLayout_3.addWidget(self.lbl_period)
        self.line_3 = QtWidgets.QFrame(parent=DaySchedule)
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_3.addWidget(self.line_3)
        self.label_10 = QtWidgets.QLabel(parent=DaySchedule)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_3.addWidget(self.label_10)
        self.lbl_dur = QtWidgets.QLabel(parent=DaySchedule)
        self.lbl_dur.setObjectName("lbl_dur")
        self.horizontalLayout_3.addWidget(self.lbl_dur)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.rb_activate = QtWidgets.QRadioButton(parent=DaySchedule)
        self.rb_activate.setChecked(True)
        self.rb_activate.setObjectName("rb_activate")
        self.horizontalLayout_5.addWidget(self.rb_activate)
        self.rb_inhibit = QtWidgets.QRadioButton(parent=DaySchedule)
        self.rb_inhibit.setChecked(False)
        self.rb_inhibit.setObjectName("rb_inhibit")
        self.horizontalLayout_5.addWidget(self.rb_inhibit)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.line = QtWidgets.QFrame(parent=DaySchedule)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.btn_sched = QtWidgets.QPushButton(parent=DaySchedule)
        self.btn_sched.setObjectName("btn_sched")
        self.horizontalLayout_4.addWidget(self.btn_sched)
        self.btn_unsched = QtWidgets.QPushButton(parent=DaySchedule)
        self.btn_unsched.setObjectName("btn_unsched")
        self.horizontalLayout_4.addWidget(self.btn_unsched)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(DaySchedule)
        QtCore.QMetaObject.connectSlotsByName(DaySchedule)

    def retranslateUi(self, DaySchedule):
        _translate = QtCore.QCoreApplication.translate
        DaySchedule.setWindowTitle(_translate("DaySchedule", "Day Schedule"))
        self.gb_d_sched.setTitle(_translate("DaySchedule", "Schedule"))
        self.gb_d_period.setTitle(_translate("DaySchedule", "Period"))
        self.label.setText(_translate("DaySchedule", "0"))
        self.label_2.setText(_translate("DaySchedule", "28 days"))
        self.gb_d_dur.setTitle(_translate("DaySchedule", "Duration"))
        self.label_3.setText(_translate("DaySchedule", "1"))
        self.label_4.setText(_translate("DaySchedule", "60 mins"))
        self.label_7.setText(_translate("DaySchedule", "Time:"))
        self.label_8.setText(_translate("DaySchedule", "Period:"))
        self.lbl_period.setText(_translate("DaySchedule", "28 days"))
        self.label_10.setText(_translate("DaySchedule", "Duration:"))
        self.lbl_dur.setText(_translate("DaySchedule", "60 mins"))
        self.rb_activate.setText(_translate("DaySchedule", "Activate"))
        self.rb_inhibit.setText(_translate("DaySchedule", "Inhibit"))
        self.btn_sched.setText(_translate("DaySchedule", "Schedule"))
        self.btn_unsched.setText(_translate("DaySchedule", "Unschedule"))
