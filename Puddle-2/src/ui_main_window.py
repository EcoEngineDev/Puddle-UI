"""Auto-generated style main window stub produced for Puddle 2.

This module mirrors the structure produced by `pyuic6` so it can be regenerated
without disrupting the application glue code.
"""

from PyQt6 import QtCore, QtWidgets


class Ui_MainWindow(object):
    """Designer-based main window layout supporting mini and expanded views."""

    def setupUi(self, MainWindow: QtWidgets.QMainWindow) -> None:
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1180, 760)
        MainWindow.setMinimumSize(QtCore.QSize(420, 200))

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.centralLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralLayout.setObjectName("centralLayout")
        self.centralLayout.setContentsMargins(12, 12, 12, 12)
        self.centralLayout.setSpacing(0)

        self.backgroundFrame = QtWidgets.QFrame(parent=self.centralwidget)
        self.backgroundFrame.setObjectName("backgroundFrame")
        self.backgroundFrame.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.backgroundFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)

        self.backgroundLayout = QtWidgets.QVBoxLayout(self.backgroundFrame)
        self.backgroundLayout.setObjectName("backgroundLayout")
        self.backgroundLayout.setContentsMargins(20, 20, 20, 20)
        self.backgroundLayout.setSpacing(0)

        self.backgroundVerticalSpacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.backgroundLayout.addItem(self.backgroundVerticalSpacer)

        self.cardPositionLayout = QtWidgets.QHBoxLayout()
        self.cardPositionLayout.setObjectName("cardPositionLayout")
        self.cardPositionLayout.setContentsMargins(0, 0, 0, 0)
        self.cardPositionLayout.setSpacing(0)

        self.mainCard = QtWidgets.QFrame(parent=self.backgroundFrame)
        self.mainCard.setObjectName("mainCard")
        self.mainCard.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.mainCard.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)

        self.cardLayout = QtWidgets.QVBoxLayout(self.mainCard)
        self.cardLayout.setObjectName("cardLayout")
        self.cardLayout.setContentsMargins(0, 0, 0, 0)
        self.cardLayout.setSpacing(0)

        self.viewStack = QtWidgets.QStackedWidget(parent=self.mainCard)
        self.viewStack.setObjectName("viewStack")

        # --- Mini page -----------------------------------------------------
        self.miniPage = QtWidgets.QWidget()
        self.miniPage.setObjectName("miniPage")
        self.miniPageLayout = QtWidgets.QVBoxLayout(self.miniPage)
        self.miniPageLayout.setObjectName("miniPageLayout")
        self.miniPageLayout.setContentsMargins(24, 20, 24, 20)
        self.miniPageLayout.setSpacing(12)

        self.miniHeaderLayout = QtWidgets.QHBoxLayout()
        self.miniHeaderLayout.setObjectName("miniHeaderLayout")
        self.miniStatusLabel = QtWidgets.QLabel(parent=self.miniPage)
        self.miniStatusLabel.setObjectName("miniStatusLabel")
        self.miniHeaderLayout.addWidget(self.miniStatusLabel)

        self.miniHeaderSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.miniHeaderLayout.addItem(self.miniHeaderSpacer)

        self.miniExpandButton = QtWidgets.QToolButton(parent=self.miniPage)
        self.miniExpandButton.setObjectName("miniExpandButton")
        self.miniExpandButton.setToolTip("Expand player")
        self.miniExpandButton.setAutoRaise(True)
        self.miniHeaderLayout.addWidget(self.miniExpandButton)

        self.miniPageLayout.addLayout(self.miniHeaderLayout)

        self.miniContentLayout = QtWidgets.QHBoxLayout()
        self.miniContentLayout.setObjectName("miniContentLayout")

        self.miniAlbumArt = QtWidgets.QLabel(parent=self.miniPage)
        self.miniAlbumArt.setObjectName("miniAlbumArt")
        self.miniAlbumArt.setMinimumSize(QtCore.QSize(80, 80))
        self.miniAlbumArt.setMaximumSize(QtCore.QSize(96, 96))
        self.miniAlbumArt.setScaledContents(True)
        self.miniContentLayout.addWidget(self.miniAlbumArt)

        self.miniTextLayout = QtWidgets.QVBoxLayout()
        self.miniTextLayout.setObjectName("miniTextLayout")
        self.miniTextLayout.setSpacing(4)

        self.miniTrackLabel = QtWidgets.QLabel(parent=self.miniPage)
        self.miniTrackLabel.setObjectName("miniTrackLabel")
        self.miniTextLayout.addWidget(self.miniTrackLabel)

        self.miniArtistLabel = QtWidgets.QLabel(parent=self.miniPage)
        self.miniArtistLabel.setObjectName("miniArtistLabel")
        self.miniTextLayout.addWidget(self.miniArtistLabel)

        self.miniContentLayout.addLayout(self.miniTextLayout)

        self.miniControlsLayout = QtWidgets.QHBoxLayout()
        self.miniControlsLayout.setObjectName("miniControlsLayout")
        self.miniControlsLayout.setSpacing(12)

        self.miniPreviousButton = QtWidgets.QToolButton(parent=self.miniPage)
        self.miniPreviousButton.setObjectName("miniPreviousButton")
        self.miniPreviousButton.setAutoRaise(True)
        self.miniControlsLayout.addWidget(self.miniPreviousButton)

        self.miniPlayPauseButton = QtWidgets.QToolButton(parent=self.miniPage)
        self.miniPlayPauseButton.setObjectName("miniPlayPauseButton")
        self.miniPlayPauseButton.setAutoRaise(True)
        self.miniControlsLayout.addWidget(self.miniPlayPauseButton)

        self.miniNextButton = QtWidgets.QToolButton(parent=self.miniPage)
        self.miniNextButton.setObjectName("miniNextButton")
        self.miniNextButton.setAutoRaise(True)
        self.miniControlsLayout.addWidget(self.miniNextButton)

        self.miniContentLayout.addLayout(self.miniControlsLayout)
        self.miniPageLayout.addLayout(self.miniContentLayout)

        self.miniProgressBar = QtWidgets.QProgressBar(parent=self.miniPage)
        self.miniProgressBar.setObjectName("miniProgressBar")
        self.miniProgressBar.setTextVisible(False)
        self.miniProgressBar.setRange(0, 1000)
        self.miniProgressBar.setValue(0)
        self.miniPageLayout.addWidget(self.miniProgressBar)

        self.viewStack.addWidget(self.miniPage)

        # --- Expanded page -------------------------------------------------
        self.expandedPage = QtWidgets.QWidget()
        self.expandedPage.setObjectName("expandedPage")
        self.expandedLayout = QtWidgets.QVBoxLayout(self.expandedPage)
        self.expandedLayout.setObjectName("expandedLayout")
        self.expandedLayout.setContentsMargins(32, 28, 32, 28)
        self.expandedLayout.setSpacing(20)

        self.expandedHeaderLayout = QtWidgets.QHBoxLayout()
        self.expandedHeaderLayout.setObjectName("expandedHeaderLayout")
        self.connectionStatusLabel = QtWidgets.QLabel(parent=self.expandedPage)
        self.connectionStatusLabel.setObjectName("connectionStatusLabel")
        self.expandedHeaderLayout.addWidget(self.connectionStatusLabel)

        self.expandedHeaderSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.expandedHeaderLayout.addItem(self.expandedHeaderSpacer)

        self.themeButton = QtWidgets.QToolButton(parent=self.expandedPage)
        self.themeButton.setObjectName("themeButton")
        self.themeButton.setToolTip("Adjust theme colours")
        self.themeButton.setAutoRaise(True)
        self.expandedHeaderLayout.addWidget(self.themeButton)

        self.collapseButton = QtWidgets.QToolButton(parent=self.expandedPage)
        self.collapseButton.setObjectName("collapseButton")
        self.collapseButton.setToolTip("Collapse to mini player")
        self.collapseButton.setAutoRaise(True)
        self.expandedHeaderLayout.addWidget(self.collapseButton)

        self.expandedLayout.addLayout(self.expandedHeaderLayout)

        self.expandedContentLayout = QtWidgets.QHBoxLayout()
        self.expandedContentLayout.setObjectName("expandedContentLayout")

        self.albumArt = QtWidgets.QLabel(parent=self.expandedPage)
        self.albumArt.setObjectName("albumArt")
        self.albumArt.setMinimumSize(QtCore.QSize(320, 320))
        self.albumArt.setScaledContents(True)
        self.expandedContentLayout.addWidget(self.albumArt)

        self.contentLayout = QtWidgets.QVBoxLayout()
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setSpacing(18)

        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLayout.setObjectName("titleLayout")
        self.trackTitleLabel = QtWidgets.QLabel(parent=self.expandedPage)
        self.trackTitleLabel.setObjectName("trackTitleLabel")
        self.titleLayout.addWidget(self.trackTitleLabel)

        self.currentTimeLabel = QtWidgets.QLabel(parent=self.expandedPage)
        self.currentTimeLabel.setObjectName("currentTimeLabel")
        self.currentTimeLabel.setMinimumSize(QtCore.QSize(60, 20))
        self.currentTimeLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.titleLayout.addWidget(self.currentTimeLabel)
        self.contentLayout.addLayout(self.titleLayout)

        self.artistLabel = QtWidgets.QLabel(parent=self.expandedPage)
        self.artistLabel.setObjectName("artistLabel")
        self.contentLayout.addWidget(self.artistLabel)

        self.progressSlider = QtWidgets.QSlider(parent=self.expandedPage)
        self.progressSlider.setObjectName("progressSlider")
        self.progressSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.progressSlider.setTracking(False)
        self.contentLayout.addWidget(self.progressSlider)

        self.durationLayout = QtWidgets.QHBoxLayout()
        self.durationLayout.setObjectName("durationLayout")
        self.remainingTimeLabel = QtWidgets.QLabel(parent=self.expandedPage)
        self.remainingTimeLabel.setObjectName("remainingTimeLabel")
        self.remainingTimeLabel.setMinimumSize(QtCore.QSize(60, 20))
        self.remainingTimeLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.durationLayout.addWidget(self.remainingTimeLabel)

        self.durationSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.durationLayout.addItem(self.durationSpacer)

        self.volumeSlider = QtWidgets.QSlider(parent=self.expandedPage)
        self.volumeSlider.setObjectName("volumeSlider")
        self.volumeSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(80)
        self.durationLayout.addWidget(self.volumeSlider)

        self.contentLayout.addLayout(self.durationLayout)

        self.controlLayout = QtWidgets.QHBoxLayout()
        self.controlLayout.setObjectName("controlLayout")

        self.controlSpacerLeft = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.controlLayout.addItem(self.controlSpacerLeft)

        self.previousButton = QtWidgets.QToolButton(parent=self.expandedPage)
        self.previousButton.setObjectName("previousButton")
        self.previousButton.setAutoRaise(True)
        self.controlLayout.addWidget(self.previousButton)

        self.playPauseButton = QtWidgets.QToolButton(parent=self.expandedPage)
        self.playPauseButton.setObjectName("playPauseButton")
        self.playPauseButton.setAutoRaise(True)
        self.controlLayout.addWidget(self.playPauseButton)

        self.nextButton = QtWidgets.QToolButton(parent=self.expandedPage)
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setAutoRaise(True)
        self.controlLayout.addWidget(self.nextButton)

        self.controlSpacerRight = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.controlLayout.addItem(self.controlSpacerRight)

        self.contentLayout.addLayout(self.controlLayout)

        self.searchLayout = QtWidgets.QHBoxLayout()
        self.searchLayout.setObjectName("searchLayout")
        self.searchField = QtWidgets.QLineEdit(parent=self.expandedPage)
        self.searchField.setObjectName("searchField")
        self.searchLayout.addWidget(self.searchField)

        self.searchButton = QtWidgets.QPushButton(parent=self.expandedPage)
        self.searchButton.setObjectName("searchButton")
        self.searchLayout.addWidget(self.searchButton)

        self.contentLayout.addLayout(self.searchLayout)

        self.queueList = QtWidgets.QListWidget(parent=self.expandedPage)
        self.queueList.setObjectName("queueList")
        self.queueList.setAlternatingRowColors(True)
        self.queueList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.contentLayout.addWidget(self.queueList)

        self.expandedContentLayout.addLayout(self.contentLayout)
        self.expandedLayout.addLayout(self.expandedContentLayout)

        self.viewStack.addWidget(self.expandedPage)

        # --- Assemble ------------------------------------------------------
        self.cardLayout.addWidget(self.viewStack)
        self.cardPositionLayout.addWidget(self.mainCard)
        self.cardPositionSpacer = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.cardPositionLayout.addItem(self.cardPositionSpacer)
        self.backgroundLayout.addLayout(self.cardPositionLayout)
        self.centralLayout.addWidget(self.backgroundFrame)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.viewStack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow: QtWidgets.QMainWindow) -> None:
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "YT Music Mini Player"))
        self.miniStatusLabel.setText(_translate("MainWindow", "Disconnected"))
        self.miniExpandButton.setText("")
        self.miniAlbumArt.setText("")
        self.miniTrackLabel.setText(_translate("MainWindow", "No track selected"))
        self.miniArtistLabel.setText(_translate("MainWindow", "Start playing to begin"))
        self.miniPreviousButton.setText("")
        self.miniPlayPauseButton.setText("")
        self.miniNextButton.setText("")
        self.connectionStatusLabel.setText(_translate("MainWindow", "Disconnected"))
        self.themeButton.setText("")
        self.collapseButton.setText("")
        self.albumArt.setText("")
        self.trackTitleLabel.setText(_translate("MainWindow", "No track selected"))
        self.currentTimeLabel.setText(_translate("MainWindow", "0:00"))
        self.artistLabel.setText(_translate("MainWindow", "Search YouTube Music to begin"))
        self.remainingTimeLabel.setText(_translate("MainWindow", "-0:00"))
        self.previousButton.setText("")
        self.playPauseButton.setText("")
        self.nextButton.setText("")
        self.searchField.setPlaceholderText(_translate("MainWindow", "Search YouTube Music..."))
        self.searchButton.setText(_translate("MainWindow", "Search"))
